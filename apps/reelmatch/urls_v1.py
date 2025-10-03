# reelmatch/urls_v1.py
#
# Version 1 API routes for Reelmatch.
# - Mocked movie endpoints (for testing/demo)
# - Favorite movies (CRUD via DRF ViewSet)
#

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FavoriteMovieViewSet
from apps.reelmatch.views_movies import (
    TrendingMoviesAPIView,
    MovieRecommendationsAPIView,
    MovieDetailsAPIView,
)

# DRF router for favorites
router = DefaultRouter()
router.register(r"favorites", FavoriteMovieViewSet, basename="favorite")

urlpatterns = [
    # Mocked movie endpoints (class-based views)
    path(
        "movies/trending/",
        TrendingMoviesAPIView.as_view(),
        name="movies-trending-mock",
    ),
    path(
        "movies/<int:movie_id>/recommendations/",
        MovieRecommendationsAPIView.as_view(),
        name="movie-recommendations-mock",
    ),
    path(
        "movies/<int:movie_id>/details/",
        MovieDetailsAPIView.as_view(),
        name="movie-details-mock",
    ),

    # Favorites endpoints (from ViewSet)
    path("", include(router.urls)),
]
