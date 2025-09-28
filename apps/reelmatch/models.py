from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()

class FavoriteMovie(models.Model):
    user = models.ForeignKey(
        User,
        related_name="favorite_movies",
        on_delete=models.CASCADE
    )
    tmdb_id = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    poster_path = models.CharField(max_length=512, blank=True, null=True)
    overview = models.TextField(blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True)

    # Optional: track how/why the movie was added
    source = models.CharField(
        max_length=50,
        choices=[
            ("manual", "Manual"),
            ("recommendation", "Recommendation"),
            ("import", "Imported"),
        ],
        default="manual",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "tmdb_id"], name="unique_user_favorite")
        ]
        ordering = ("-added_at",)
        indexes = [
            models.Index(fields=["user", "tmdb_id"]),
            models.Index(fields=["added_at"]),
        ]

    def __str__(self):
        return f"{getattr(self.user, 'username', 'Unknown')} - {self.title} ({self.tmdb_id})"
