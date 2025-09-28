# api_helper.py
#
# Production-ready CLI helper for your Reelmatch API.
# Handles login + auto-refresh tokens, and supports commands like:
#   python3 api_helper.py favorites list
#   python3 api_helper.py favorites add 550
#   python3 api_helper.py favorites delete 2
#   python3 api_helper.py movies trending
#   python3 api_helper.py movies recommendations 550

import os
import sys
import requests
from tabulate import tabulate

API_URL = "http://127.0.0.1:8000"
# API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


# 🔑 configure your credentials here (for /auth/token/)
USERNAME = "king"
PASSWORD = "123456"

# Token cache (so we don't log in every time)
TOKEN_FILE = ".apitoken"


# -------------------- Auth Helpers --------------------
def get_token():
    """Get a valid access token (reuse cached one if possible)."""
    token = None

    # Check if token is cached
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            token = f.read().strip()

    # Validate cached token
    if token:
        r = requests.get(f"{API_URL}/api/favorites/", headers={"Authorization": f"Bearer {token}"})
        if r.status_code == 200:
            return token  # still valid
        else:
            print("⚠️  Cached token expired, logging in again...")

    # Login to get a new token
    r = requests.post(
        f"{API_URL}/auth/token/",
        json={"username": USERNAME, "password": PASSWORD},
    )
    if r.status_code != 200:
        sys.exit(f"❌ Failed to authenticate: {r.text}")
    token = r.json()["access"]

    # Save token to file
    with open(TOKEN_FILE, "w") as f:
        f.write(token)

    print("✅ Logged in, got new access token.")
    return token


def call_api(method, endpoint, **kwargs):
    """Helper to call API with authentication + auto-retry."""
    token = get_token()
    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {token}"
    headers["Content-Type"] = "application/json"

    url = f"{API_URL}{endpoint}"
    r = requests.request(method, url, headers=headers, **kwargs)

    # Retry once if unauthorized
    if r.status_code == 401:
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)
        token = get_token()
        headers["Authorization"] = f"Bearer {token}"
        r = requests.request(method, url, headers=headers, **kwargs)

    if r.status_code >= 400:
        sys.exit(f"❌ API error {r.status_code}: {r.text}")

    return r.json() if r.text else {}


# -------------------- Favorites --------------------
def favorites_list():
    data = call_api("GET", "/api/favorites/")
    if not data:
        print("📭 No favorites found.")
        return
    table = [(f["id"], f["tmdb_id"], f["title"]) for f in data]
    print(tabulate(table, headers=["ID", "TMDb ID", "Title"]))


def favorites_add(tmdb_id):
    data = call_api("POST", "/api/favorites/", json={"tmdb_id": int(tmdb_id)})
    print(f"⭐ Added favorite: {data.get('title', 'Unknown')} (tmdb_id={data['tmdb_id']})")


def favorites_delete(fav_id):
    call_api("DELETE", f"/api/favorites/{fav_id}/")
    print(f"🗑️ Deleted favorite with id {fav_id}")


# -------------------- Movies --------------------


def movies_trending():
    data = call_api("GET", "/movies/trending/")
    results = data.get("results", [])
    if not results:
        print("📭 No trending movies found.")
        return
    table = [(m["id"], m["title"], m.get("release_date", "N/A")) for m in results[:10]]
    print(tabulate(table, headers=["ID", "Title", "Release Date"]))


def movies_recommendations(tmdb_id):
    data = call_api("GET", f"/movies/{tmdb_id}/recommendations/")
    results = data.get("results", [])
    if not results:
        print("📭 No recommendations found.")
        return
    table = [(m["id"], m["title"], m.get("release_date", "N/A")) for m in results[:10]]
    print(tabulate(table, headers=["ID", "Title", "Release Date"]))


# -------------------- CLI Entrypoint --------------------
def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 api_helper.py favorites list")
        print("  python3 api_helper.py favorites add <tmdb_id>")
        print("  python3 api_helper.py favorites delete <id>")
        print("  python3 api_helper.py movies trending")
        print("  python3 api_helper.py movies recommendations <movie_id>")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "favorites":
        if len(sys.argv) == 3 and sys.argv[2] == "list":
            favorites_list()
        elif len(sys.argv) == 4 and sys.argv[2] == "add":
            favorites_add(sys.argv[3])
        elif len(sys.argv) == 4 and sys.argv[2] == "delete":
            favorites_delete(sys.argv[3])
        else:
            sys.exit("Usage: python3 api_helper.py favorites [list|add <tmdb_id>|delete <id>]")

    elif cmd == "movies":
        if len(sys.argv) == 3 and sys.argv[2] == "trending":
            movies_trending()
        elif len(sys.argv) == 4 and sys.argv[2] == "recommendations":
            movies_recommendations(sys.argv[3])
        else:
            sys.exit("Usage: python3 api_helper.py movies [trending|recommendations <movie_id>]")

    else:
        sys.exit(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
