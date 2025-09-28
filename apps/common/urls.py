# apps/common/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Example placeholder
    path("health/", views.health_check, name="health_check"),
]
