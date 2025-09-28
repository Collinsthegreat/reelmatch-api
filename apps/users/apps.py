from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users"   # full Python path
    label = "users"       # short label (used in migrations and db table names)
