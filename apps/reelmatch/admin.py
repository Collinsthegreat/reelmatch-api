from django.contrib import admin

# Register your models here.
# reelmatch/admin.py
#
# Registers the FavoriteMovie model in the Django admin
# so you can view and manage saved favorites from the admin UI.

from django.contrib import admin
from .models import FavoriteMovie


@admin.register(FavoriteMovie)
class FavoriteMovieAdmin(admin.ModelAdmin):
    """
    Admin configuration for the FavoriteMovie model.
    This controls how favorite movies appear in the Django admin site.
    """

    # Fields shown in the list view (like table columns)
    list_display = ("user", "title", "tmdb_id", "added_at")

    # Enable search by movie title, username, or TMDb ID
    search_fields = ("title", "user__username", "tmdb_id")

    # Order records by newest favorites first
    ordering = ("-added_at",)

    # Prevent manual edits to added_at in admin detail view
    readonly_fields = ("added_at",)
