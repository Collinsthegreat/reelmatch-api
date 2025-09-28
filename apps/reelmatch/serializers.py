# reelmatch/serializers.py

from rest_framework import serializers
from .models import FavoriteMovie


class FavoriteMovieSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying favorite movies.
    Used when returning data to the client (GET requests).
    """
    class Meta:
        model = FavoriteMovie
        fields = ["id", "tmdb_id", "title", "poster_path", "overview", "added_at"]
        read_only_fields = ["id", "title", "poster_path", "overview", "added_at"]


class FavoriteMovieCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new favorite movies.
    Clients only provide the TMDb movie ID, but
    the response will also include the generated ID.
    """
    tmdb_id = serializers.IntegerField(
        help_text="TMDb movie ID (must be positive integer)."
    )

    class Meta:
        model = FavoriteMovie
        fields = ["id", "tmdb_id"]  # ✅ include id in response
        read_only_fields = ["id"]

    def validate_tmdb_id(self, value):
        if value <= 0:
            raise serializers.ValidationError("TMDb ID must be a positive integer.")
        return value
