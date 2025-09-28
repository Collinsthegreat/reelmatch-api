# apps/reelmatch/views_movies.py
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Mocked movie data for testing
MOCK_TRENDING = [
    {"id": 101, "title": "The Matrix"},
    {"id": 102, "title": "Inception"},
    {"id": 103, "title": "Interstellar"},
]

MOCK_RECOMMENDATIONS = {
    101: [{"id": 201, "title": "The Matrix Reloaded"}],
    202: [{"id": 2021, "title": "The Dark Knight"}],
    550: [{"id": 5501, "title": "Fight Club Sequel"}],
}

MOCK_DETAILS = {
    123: {"id": 123, "title": "Titanic", "year": 1997},
    456: {"id": 456, "title": "Avatar", "year": 2009},
    789: {"id": 789, "title": "Gladiator", "year": 2000},
}


@api_view(["GET"])
def trending_movies(request):
    return Response({"results": MOCK_TRENDING})


@api_view(["GET"])
def recommendations_movies(request, movie_id: int):
    data = MOCK_RECOMMENDATIONS.get(movie_id, [])
    return Response({"results": data})


@api_view(["GET"])
def movie_details(request, movie_id: int):
    data = MOCK_DETAILS.get(movie_id, {})
    return Response(data)
