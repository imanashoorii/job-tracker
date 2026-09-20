from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("core")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

GENERAL_RETRY_POLICY = {
    "autoretry_for": (Exception,),
    "retry_backoff": 2,
    "retry_jitter": True,
    "retry_kwargs": {"max_retries": 3, "countdown": 10},
}


DEFAULT_QUEUE = "default"
