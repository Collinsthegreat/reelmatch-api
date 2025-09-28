# reelmatch/urls_v1.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FavoriteMovieViewSet
from apps.reelmatch import views_movies

# DRF router for favorites
router = DefaultRouter()
router.register(r"favorites", FavoriteMovieViewSet, basename="favorite")

urlpatterns = [
    # Movie endpoints (mocked views for tests)
    path("movies/trending/", views_movies.trending_movies, name="movies-trending"),
    path(
        "movies/<int:movie_id>/recommendations/",
        views_movies.recommendations_movies,
        name="movie-recommendations",
    ),
    path(
        "movies/<int:movie_id>/details/",
        views_movies.movie_details,
        name="movie-details",
    ),

    # Favorites endpoints (from ViewSet)
    path("", include(router.urls)),
]
