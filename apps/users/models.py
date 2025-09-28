from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom User model.
    Extend this with extra fields as needed (e.g., profile_picture, bio, etc.)
    """
    # Example extra field
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.username
