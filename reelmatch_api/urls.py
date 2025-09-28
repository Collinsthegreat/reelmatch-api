"""
URL configuration for reelmatch_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# reelmatch_api/urls.py
#
# Project-level URL configuration.
# Connects:
# - Admin
# - JWT authentication
# - API schema (OpenAPI/Swagger)
# - Reelmatch app routes

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView   # 👈 needed for redirect

# drf-spectacular for API schema + Swagger docs
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

# JWT views from DRF SimpleJWT
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # Django admin panel
    path("admin/", admin.site.urls),

    # JWT authentication endpoints
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),   # login
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"), # refresh access token

    # API schema + Swagger docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),  # OpenAPI schema
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),  # Swagger UI

    # App-level routes
    path("", include("apps.reelmatch.urls")),

     # Versioned API entrypoint
    path("api/v1/", include("apps.reelmatch.urls_v1")),

    # Redirect root "/" to Swagger docs
    path("", RedirectView.as_view(url="/api/docs/", permanent=False)),

    path("api/v1/users/", include("apps.users.urls")),

]
