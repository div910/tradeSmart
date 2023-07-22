import os
from celery import Celery as _Celery
from django.apps import AppConfig
from django.conf import settings

os.environ.setdefault('DEFAULT_SETTINGS_MODULE', 'settings')

app = _Celery(settings.CELERY_APP_NAME, broker='redis://127.0.0.1:6379')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

class CeleryAppConfig(AppConfig):
    name = 'celery_app'