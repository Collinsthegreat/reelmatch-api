# reelmatch_api/celery.py
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reelmatch_api.settings")

app = Celery("reelmatch_api")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
