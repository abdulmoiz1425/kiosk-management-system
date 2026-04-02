import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wafaatech.settings')

app = Celery('wafaatech')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
