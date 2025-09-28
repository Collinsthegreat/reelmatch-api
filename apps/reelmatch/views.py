# reelmatch/views.py
"""
Views (API Layer) for Reelmatch.

Responsibilities:
- Expose clean, documented API endpoints.
- Handle authentication & permissions.
- Call service layer (tmdb.py) for external API interactions.
- Handle error responses gracefully.
- Serialize/deserialize data using DRF serializers.
"""

import os
from rest_framework import status, viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from apps.reelmatch.throttles import TMDBRateThrottle

from drf_spectacular.utils import (
    extend_schema,
    OpenApiTypes,
    OpenApiParameter,
)

from .tmdb import (
    get_trending,
    get_recommendations,
    get_movie_details,
    search_movies,
)
from .models import FavoriteMovie
from .serializers import FavoriteMovieSerializer, FavoriteMovieCreateSerializer

# Cache duration for TMDb endpoints (default: 60s, can override via env)
CACHE_SECONDS = int(os.getenv("TMDB_CACHE_SECONDS", 60))


class TrendingMoviesAPIView(APIView):
    """
    Public endpoint: returns trending movies from TMDb.
    Cached for CACHE_SECONDS to reduce external API calls.
    Supports pagination via ?page=
    """
    permission_classes = [permissions.AllowAny]
    throttle_classes = [TMDBRateThrottle]

    @method_decorator(cache_page(CACHE_SECONDS))
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="page",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Page number for paginated results (default=1)",
            )
        ],
        responses={200: OpenApiTypes.OBJECT, 502: OpenApiTypes.OBJECT},
        description="Return TMDb trending movies (cached, paginated).",
    )
    def get(self, request):
        page = int(request.query_params.get("page", 1))
        data = get_trending(page=page)
        if "error" in data:
            return Response(
                {"detail": "Failed to fetch trending movies", "error": data["error"]},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(data)


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="movie_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="TMDb movie ID",
            required=True,
        ),
        OpenApiParameter(
            name="page",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Page number for recommendations (default=1)",
        ),
    ],
    responses={200: OpenApiTypes.OBJECT, 502: OpenApiTypes.OBJECT},
    description="Return TMDb recommendations for a given movie ID (paginated).",
)
class MovieRecommendationsAPIView(APIView):
    """
    Public endpoint: returns recommendations for a given TMDb movie ID.
    Cached for CACHE_SECONDS.
    Supports pagination via ?page=
    """
    permission_classes = [permissions.AllowAny]

    @method_decorator(cache_page(CACHE_SECONDS))
    def get(self, request, movie_id: int):
        page = int(request.query_params.get("page", 1))
        data = get_recommendations(movie_id, page=page)
        if "error" in data:
            return Response(
                {"detail": "Failed to fetch recommendations", "error": data["error"]},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(data)


class MovieSearchAPIView(APIView):
    """
    Public endpoint: search TMDb for movies by query string.
    Example: /api/movies/search/?query=Matrix&page=2
    """
    permission_classes = [permissions.AllowAny]
    throttle_classes = [TMDBRateThrottle]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="query",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Search query (movie title)",
                required=True,
            ),
            OpenApiParameter(
                name="page",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Page number for paginated results (default=1)",
            ),
        ],
        responses={200: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT},
        description="Search for movies on TMDb by title.",
    )
    def get(self, request):
        query = request.query_params.get("query")
        page = int(request.query_params.get("page", 1))
        if not query:
            return Response(
                {"detail": "Query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = search_movies(query=query, page=page)
        if "error" in data:
            return Response(
                {"detail": "Failed to search movies", "error": data["error"]},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(data)


class FavoriteMovieViewSet(viewsets.ModelViewSet):
    """
    Authenticated endpoint: manages a user's favorite movies.
    - list: return logged-in user's favorites
    - create: add a new favorite (with TMDb snapshot if available)
    - destroy: remove a favorite
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FavoriteMovieSerializer

    # 👇 Explicitly tell DRF & drf-spectacular that pk = integer ID
    lookup_field = "id"
    lookup_value_regex = r"\d+"  # ensures it's treated as an integer in schema/docs

    def get_queryset(self):
        """
        Limit results to this user's favorites only.
        Use `.only()` to fetch minimal fields from DB for performance.
        """
        return FavoriteMovie.objects.filter(user=self.request.user).only(
            "tmdb_id", "title", "poster_path", "added_at"
        )

    def get_serializer_class(self):
        """
        Use lightweight serializer for creation,
        full serializer for reads.
        """
        if self.action == "create":
            return FavoriteMovieCreateSerializer
        return FavoriteMovieSerializer

    def perform_create(self, serializer):
        """
        On create:
        - Call TMDb service to fetch movie metadata.
        - If TMDb fails, still save with minimal info (fallback title).
        """
        tmdb_id = serializer.validated_data["tmdb_id"]
        details = get_movie_details(tmdb_id)

        if "error" in details:
            serializer.save(user=self.request.user, title=f"tmdb:{tmdb_id}")
            return

        serializer.save(
            user=self.request.user,
            title=details.get("title") or details.get("name") or "",
            poster_path=details.get("poster_path", ""),
            overview=details.get("overview", ""),
        )

    def destroy(self, request, *args, **kwargs):
        """
        Explicitly override destroy to ensure DELETE returns 204.
        """
        return super().destroy(request, *args, **kwargs)
