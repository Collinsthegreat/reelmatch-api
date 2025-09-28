# apps/reelmatch/tests/test_movies.py
import pytest

@pytest.mark.django_db
def test_trending_movies(api_client):
    """
    Public trending movies endpoint should return mocked trending data.
    """
    resp = api_client.get("/api/v1/movies/trending/")
    assert resp.status_code == 200
    data = resp.json()
    assert "results" in data
    assert isinstance(data["results"], list)


@pytest.mark.parametrize("movie_id", [101, 202, 550])
@pytest.mark.django_db
def test_recommendations_movies(api_client, movie_id):
    """
    Public recommendations endpoint should return mocked recommendations
    for different movie IDs.
    """
    resp = api_client.get(f"/api/v1/movies/{movie_id}/recommendations/")
    assert resp.status_code == 200
    data = resp.json()
    assert "results" in data
    assert isinstance(data["results"], list)


@pytest.mark.parametrize("movie_id", [123, 456, 789])
@pytest.mark.django_db
def test_movie_details(api_client, movie_id):
    """
    Public movie details endpoint should return mocked movie details
    for different movie IDs.
    """
    resp = api_client.get(f"/api/v1/movies/{movie_id}/details/")
    assert resp.status_code == 200
    data = resp.json()
    assert "id" in data
    assert data["id"] == movie_id
    assert "title" in data
