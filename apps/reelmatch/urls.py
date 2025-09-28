# reelmatch/urls.py
#
# URL routing for the reelmatch app.
#
# This file defines endpoints for:
# 1. Trending movies (via TMDb)
# 2. Movie recommendations (via TMDb)
# 3. Movie search (via TMDb)
# 4. User favorite movies (CRUD via DRF ViewSet)
#
# DRF router automatically generates RESTful routes for the FavoriteMovieViewSet.
# Example:
#   - GET    /api/favorites/        → list all favorites
#   - POST   /api/favorites/        → add a favorite
#   - GET    /api/favorites/{id}/   → retrieve a specific favorite
#   - PUT    /api/favorites/{id}/   → update a favorite
#   - DELETE /api/favorites/{id}/   → delete a favorite
#
# Additional endpoints:
#   - GET /movies/trending/?page=1
#   - GET /movies/{movie_id}/recommendations/?page=1
#   - GET /movies/search/?query=<title>&page=1
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

# Define URL patterns
urlpatterns = [
    # TMDb endpoints
    path(
        "movies/trending/",
        TrendingMoviesAPIView.as_view(),
        name="movies-trending"
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
