# tests/conftest.py
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user(db):
    def _create(username="testuser", password="password"):
        user = User.objects.create_user(username=username, password=password)
        return user
    return _create


@pytest.fixture
def auth_client(api_client, create_user):
    """
    Returns an APIClient already authorized with a valid access token for tests.
    - Creates a user and fetches access token via /auth/token/
    """
    username = "king"
    password = "123456"
    user = create_user(username=username, password=password)

    # request token
    resp = api_client.post("/auth/token/", {"username": username, "password": password}, format="json")
    assert resp.status_code == 200, f"Failed to obtain token: {resp.status_code} {resp.content}"
    access = resp.json().get("access")
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    return api_client


@pytest.fixture(autouse=True)
def mock_tmdb(monkeypatch):
    """
    Global fixture that stubs the reelmatch.tmdb functions used by views:
    - get_trending(page=1)
    - get_recommendations(movie_id, page=1)
    - get_movie_details(movie_id)
    Tests can override monkeypatch behavior if necessary.
    """
    # example trending payload
    sample_trending = {
        "page": 1,
        "results": [
            {"id": 1, "title": "Mock Movie 1", "release_date": "2025-01-01"},
            {"id": 2, "title": "Mock Movie 2", "release_date": "2025-02-01"},
        ],
    }

    def sample_recommendations(movie_id):
        return {
            "page": 1,
            "results": [
                {"id": 10 + movie_id, "title": f"Recs for {movie_id}", "release_date": "2025-03-01"},
            ],
        }

    def sample_movie_details(movie_id):
        return {
            "id": movie_id,
            "title": f"Movie {movie_id}",
            "poster_path": "/fake.jpg",
            "overview": "A mocked description",
        }

    # patch functions in your module path
    import apps.reelmatch.tmdb as tmdb_mod

    # IMPORTANT: match real signatures
    monkeypatch.setattr(tmdb_mod, "get_trending", lambda page=1: sample_trending)
    monkeypatch.setattr(tmdb_mod, "get_recommendations", lambda mid, page=1: sample_recommendations(mid))
    monkeypatch.setattr(tmdb_mod, "get_movie_details", lambda mid: sample_movie_details(mid))

    yield
