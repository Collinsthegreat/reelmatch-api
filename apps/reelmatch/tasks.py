# reelmatch/tasks.py
"""
Celery tasks to pre-warm TMDb caches.
This ensures the first API request is fast and reduces load on TMDb.
"""

import logging
from celery import shared_task
from django.core.cache import cache
from .tmdb import get_trending, get_movie_details

logger = logging.getLogger(__name__)

CACHE_PREFIX = "tmdb"


@shared_task(
    bind=True,
    autoretry_for=(Exception,),  # auto-retry if any error
    retry_backoff=True,          # exponential backoff (2s, 4s, 8s…)
    retry_kwargs={"max_retries": 3},  # stop after 3 tries
)
def warm_trending_cache(self, pages: int = 2):
    """
    Pre-warm the cache for trending movies.
    By default warms the first `pages` of results.
    """
    for p in range(1, pages + 1):
        data = get_trending(media_type="movie", time_window="day")  # you can tune params
        cache_key = f"{CACHE_PREFIX}:trending:page:{p}:v1"
        cache.set(cache_key, data, timeout=60 * 30)  # 30 min
        logger.info("Warmed trending cache (page=%s)", p)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def warm_movie_details(self, movie_ids: list[int]):
    """
    Pre-warm the cache for a list of specific movies.
    Useful for popular or featured titles.
    """
    for mid in movie_ids:
        details = get_movie_details(mid)
        cache_key = f"{CACHE_PREFIX}:movie:{mid}:details:v1"
        cache.set(cache_key, details, timeout=60 * 60 * 24)  # 24h
        logger.info("Warmed movie details cache (id=%s)", mid)
