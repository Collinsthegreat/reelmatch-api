# reelmatch/tmdb.py
"""
TMDb service layer with:
- Django caching (via django-redis in production) to avoid repeated API calls
- Centralized session with retry/backoff for transient errors
- Explicit handling of TMDb 429 (rate limit) responses
- DTO normalizer to give the frontend a stable, compact schema

Design:
- This layer ONLY talks to TMDb.
- It never raises exceptions → always returns dicts, either data or {"error": ...}.
- Views/serializers decide how to expose these results to clients.
"""

import os
import logging
from typing import Dict, Any, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from django.core.cache import cache

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
TMDB_BASE = "https://api.themoviedb.org/3"
DEFAULT_LANGUAGE = os.getenv("TMDB_LANGUAGE", "en-US")
CACHE_TIMEOUT = int(os.getenv("TMDB_CACHE_SECONDS", 60))  # seconds

# ---------------------------------------------------------------------------
# HTTP Session with retry/backoff
# ---------------------------------------------------------------------------
SESSION = requests.Session()
SESSION.headers.update({"Accept": "application/json"})
retries = Retry(
    total=3,                 # max retry attempts
    backoff_factor=0.6,      # exponential backoff (0.6, 1.2, 2.4s)
    status_forcelist=(500, 502, 503, 504),  # retry only on server errors
    allowed_methods=frozenset(["GET", "POST"])
)
SESSION.mount("https://", HTTPAdapter(max_retries=retries))
SESSION.mount("http://", HTTPAdapter(max_retries=retries))

# ---------------------------------------------------------------------------
# Low-level GET wrapper
# ---------------------------------------------------------------------------
def _tmdb_get(path: str, params: Optional[Dict[str, Any]] = None,
              cache_key: Optional[str] = None, timeout: int = 10) -> Dict[str, Any]:
    """
    Perform a GET request to TMDb API.
    - Adds API key & language
    - Uses retries/backoff for transient errors
    - Detects TMDb rate-limit (429)
    - Optionally caches results in Redis

    Returns: dict (payload or {"error": ..., "status_code": ...})
    """
    if not TMDB_API_KEY:
        return {"error": "TMDB_API_KEY not set", "status_code": None}

    # Apply defaults
    params = dict(params or {})
    params.update({"api_key": TMDB_API_KEY, "language": DEFAULT_LANGUAGE})

    # Try cache first
    if cache_key:
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

    url = f"{TMDB_BASE}{path}"
    try:
        resp = SESSION.get(url, params=params, timeout=timeout)
    except requests.RequestException as exc:
        logger.exception("TMDb network error: %s %s", url, exc)
        return {"error": "network_error", "status_code": None, "detail": str(exc)}

    # Explicit rate limit handling
    if resp.status_code == 429:
        retry_after = resp.headers.get("Retry-After")
        logger.warning("TMDb rate limited: %s retry-after=%s", url, retry_after)
        return {"error": "rate_limited", "status_code": 429, "retry_after": retry_after}

    try:
        resp.raise_for_status()
    except requests.HTTPError as exc:
        logger.error("TMDb HTTP error %s: %s", resp.status_code, resp.text)
        return {"error": "http_error", "status_code": resp.status_code, "detail": resp.text}

    try:
        data = resp.json()
    except ValueError:
        logger.exception("Invalid JSON from TMDb: %s", url)
        return {"error": "invalid_json", "status_code": resp.status_code}

    # Save in cache
    if cache_key:
        cache.set(cache_key, data, CACHE_TIMEOUT)

    return data

# ---------------------------------------------------------------------------
# DTO normalizer
# ---------------------------------------------------------------------------
def to_movie_dto(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize TMDb movie/TV objects to a stable, compact DTO.
    This insulates frontend from TMDb schema changes.
    """
    title = raw.get("title") or raw.get("name") or ""
    return {
        "id": raw.get("id"),
        "title": title,
        "poster": raw.get("poster_path"),
        "backdrop": raw.get("backdrop_path"),
        "release_date": raw.get("release_date") or raw.get("first_air_date"),
        "overview": raw.get("overview", ""),
        "score": raw.get("vote_average", 0.0),
    }

# ---------------------------------------------------------------------------
# Public API functions
# ---------------------------------------------------------------------------
def get_trending(
    media_type: str = "movie",
    time_window: str = "week",
    page: int = 1,
) -> Dict[str, Any]:
    """
    Fetch trending content from TMDb, normalized to DTO.
    Args:
        media_type: "movie" or "tv"
        time_window: "day" or "week"
        page: page number for pagination
    """
    cache_key = f"tmdb:trending:{media_type}:{time_window}:page:{page}"
    payload = _tmdb_get(
        f"/trending/{media_type}/{time_window}",
        params={"page": page},
        cache_key=cache_key,
    )
    if "error" in payload:
        return payload
    return {
        "page": payload.get("page", 1),
        "total_pages": payload.get("total_pages", 1),
        "results": [to_movie_dto(r) for r in payload.get("results", [])],
    }


def get_recommendations(movie_id: int, page: int = 1) -> Dict[str, Any]:
    """
    Fetch recommended movies from TMDb for a given movie ID.
    Results are normalized to DTOs.
    """
    cache_key = f"tmdb:recommendations:{movie_id}:p{page}"
    payload = _tmdb_get(f"/movie/{movie_id}/recommendations",
                        params={"page": page}, cache_key=cache_key)
    if "error" in payload:
        return payload
    return {
        "page": payload.get("page", page),
        "total_pages": payload.get("total_pages", 1),
        "results": [to_movie_dto(r) for r in payload.get("results", [])],
    }

def get_movie_details(movie_id: int) -> Dict[str, Any]:
    """
    Fetch full details for a specific movie, normalized to DTO.
    """
    cache_key = f"tmdb:movie:{movie_id}:details"
    payload = _tmdb_get(f"/movie/{movie_id}", cache_key=cache_key)
    if "error" in payload:
        return payload
    return to_movie_dto(payload)

def search_movies(query: str, page: int = 1) -> Dict[str, Any]:
    """
    Search TMDb for movies by query string, normalized to DTOs.
    """
    if not query:
        return {"error": "missing_query", "status_code": 400}

    cache_key = f"tmdb:search:{query.lower().strip()}:p{page}"
    payload = _tmdb_get(
        "/search/movie",
        params={"query": query, "page": page},
        cache_key=cache_key,
    )
    if "error" in payload:
        return payload
    return {
        "page": payload.get("page", page),
        "total_pages": payload.get("total_pages", 1),
        "results": [to_movie_dto(r) for r in payload.get("results", [])],
    }
