from __future__ import unicode_literals, absolute_import
import os

from celery import Celery
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'product_analyzer.settings')

app = Celery('product_analyzer')
app.conf.enable_utc = False

app.conf.update(timezone = 'Asia/Kolkata')

app.config_from_object(settings, namespace='CELERY')

# Celery Beat Settings
app.conf.beat_schedule = {
    'Category-Scrapper': {
        'task': 'user.tasks.categoryScrapper',
        'schedule': crontab(hour="16", minute="08"),
    },
    'Product-Scrapper': {
        'task': 'user.tasks.productScrapper',
        'schedule': crontab(hour="14", minute="27")
    }
}

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')