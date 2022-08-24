import os

from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tdp.settings")

app = Celery("tdp")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
