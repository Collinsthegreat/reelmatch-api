from django.apps import AppConfig

class CommonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.common"      # full Python path
    label = "apps_common"     # unique label (avoid clashes with "common")
