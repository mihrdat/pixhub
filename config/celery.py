import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.main.dev")

celery = Celery("pixhub")
celery.config_from_object("django.conf:settings", namespace="CELERY")
celery.autodiscover_tasks()
