from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery.schedules import crontab
import os
from kombu import Exchange, Queue


# set the default Django settings module for the 'celery' program.
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'watching_hollywood.settings')


class Config:

    broker_url = 'redis://localhost:6379/2'
    # result_backend = 'db+postgresql://'+settings.CRED['db_user']+':'+settings.CRED['db_password']+'@'+settings.CRED['db_host']+':5432'+'/'+settings.CRED['db_name']
    # result_backend = 'redis://localhost:6379/3'
    result_backend = 'django-db'
    result_cache_max = 1000
    worker_concurrency = 8
    beat_max_loop_interval = 600
    task_compression = 'gzip'
    result_compression = 'gzip'
    task_default_queue = 'low'
    result_persistent = True
    task_track_started = True
    task_publish_retry = True
    task_publish_retry_policy = {
        'max_retries': 3,
        'interval_start': 0.2,
        'interval_step': 0.2,
        'interval_max': 1,
    }
    beat_scheduler = 'django_celery_beat.schedulers:DatabaseScheduler'

    beat_schedule = {

        'data_builder': {
            'task': 'main.tasks.data_builder',
            'schedule': crontab(hour=5, minute=5),
        },

    }

    task_queues = (

        Queue('low', Exchange('low'), routing_key='low'),

        Queue('medium', Exchange('medium'), routing_key='medium'),

        Queue('high', Exchange('high'), routing_key='high'),

        Queue('metered', Exchange('metered'), routing_key='metered'),
    )

    task_routes = {

        'main.tasks.data_builder': 'high',
        'main.tasks.pull_page': 'metered',
    }


celery_app = Celery('watching_hollywood')
celery_app.config_from_object(Config)
celery_app.autodiscover_tasks()
