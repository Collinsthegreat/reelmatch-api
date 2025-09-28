# apps/reelmatch/apps.py
from django.apps import AppConfig

class ReelmatchConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.reelmatch"   # ✅ new Python path
    label = "reelmatch"       # ✅ keep same label for migration continuity
