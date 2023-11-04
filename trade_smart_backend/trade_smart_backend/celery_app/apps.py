import os
from celery import Celery as _Celery
from django.apps import AppConfig
from django.conf import settings

os.environ.setdefault('DEFAULT_SETTINGS_MODULE', 'settings')

app = _Celery(settings.CELERY_APP_NAME, broker='redis://redis:6379/0')

app.config_from_object('django.conf:settings')

app.conf.beat_schedule = settings.CELERY_BEAT_SCHEDULE

app.autodiscover_tasks()

class CeleryAppConfig(AppConfig):
    name = 'celery_app'