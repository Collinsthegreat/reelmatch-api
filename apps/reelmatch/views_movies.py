# apps/reelmatch/views_movies.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

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


class TrendingMoviesAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        responses={200: OpenApiTypes.OBJECT},
        description="Return a mocked list of trending movies."
    )
    def get(self, request):
        return Response({"results": MOCK_TRENDING})


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="movie_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="Movie ID for fetching recommendations",
            required=True,
        ),
    ],
    responses={200: OpenApiTypes.OBJECT},
    description="Return mocked recommendations for a given movie ID."
)
class MovieRecommendationsAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, movie_id: int):
        data = MOCK_RECOMMENDATIONS.get(movie_id, [])
        return Response({"results": data})


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="movie_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="Movie ID for fetching details",
            required=True,
        ),
    ],
    responses={200: OpenApiTypes.OBJECT, 404: OpenApiTypes.OBJECT},
    description="Return mocked movie details by ID."
)
class MovieDetailsAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, movie_id: int):
        data = MOCK_DETAILS.get(movie_id)
        if not data:
            return Response(
                {"detail": "Movie not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(data)
