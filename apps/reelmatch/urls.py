# reelmatch/urls.py
#
# Main API routes for Reelmatch.
# - TMDb-backed endpoints (production-ready)
# - User favorite movies (CRUD)
#

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TrendingMoviesAPIView,
    MovieRecommendationsAPIView,
    MovieSearchAPIView,
    FavoriteMovieViewSet,
)

# Initialize DRF router
router = DefaultRouter()
router.register(r"favorites", FavoriteMovieViewSet, basename="favorite")

urlpatterns = [
    # TMDb endpoints (real API)
    path(
        "movies/trending/",
        TrendingMoviesAPIView.as_view(),
        name="movies-trending",
    ),
    path(
        "movies/<int:movie_id>/recommendations/",
        MovieRecommendationsAPIView.as_view(),
        name="movie-recommendations",
    ),
    path(
        "movies/search/",
        MovieSearchAPIView.as_view(),
        name="movie-search",
    ),

    # Favorites endpoints (provided by DRF router)
    path("api/", include(router.urls)),
]
