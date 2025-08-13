import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agrisat.settings.development')

app = Celery('agrisat')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery beat schedule for periodic tasks
app.conf.beat_schedule = {
    'fetch-weather-data': {
        'task': 'apps.weather.tasks.fetch_weather_data_for_all_fields',
        'schedule': 3600.0,  # Run every hour
    },
    'update-crop-health': {
        'task': 'apps.satellites.tasks.update_crop_health_data',
        'schedule': 86400.0,  # Run daily
    },
    'check-fire-alerts': {
        'task': 'apps.disasters.tasks.check_fire_alerts',
        'schedule': 1800.0,  # Run every 30 minutes
    },
    'cleanup-old-data': {
        'task': 'apps.analytics.tasks.cleanup_old_data',
        'schedule': 604800.0,  # Run weekly
    },
}

app.conf.timezone = 'UTC'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')