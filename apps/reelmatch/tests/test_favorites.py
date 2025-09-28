# tests/test_favorites.py
import pytest


@pytest.mark.django_db
def test_favorites_crud(auth_client):
    client = auth_client

    # 1. Initially empty (paginated response)
    resp = client.get("/api/favorites/")
    assert resp.status_code == 200
    data = resp.json()
    assert "results" in data
    assert data["count"] == 0
    assert data["results"] == []

    # 2. Create favorite (tmdb_id 550)
    resp = client.post("/api/favorites/", {"tmdb_id": 550}, format="json")
    assert resp.status_code in (200, 201)
    created = resp.json()
    assert created["tmdb_id"] == 550
    fav_id = created["id"]

    # 3. List favorites contains it
    resp = client.get("/api/favorites/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 1
    assert any(f["tmdb_id"] == 550 for f in data["results"])

    # 4. Delete favorite by ID
    resp = client.delete(f"/api/favorites/{fav_id}/")
    assert resp.status_code in (204, 200)

    # 5. Verify deletion
    resp = client.get("/api/favorites/")
    data = resp.json()
    assert data["count"] == 0
    assert data["results"] == []
