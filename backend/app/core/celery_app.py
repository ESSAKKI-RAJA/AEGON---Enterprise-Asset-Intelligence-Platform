import os
from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

# Initialize Celery
# We use Redis for both broker and result backend as per Enterprise Architecture
celery_app = Celery(
    "aegon_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.analytics_worker", "app.workers.report_worker"]
)

# Optional configuration, see the application user guide.
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],  # Ignore other content
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    worker_concurrency=4, # adjust based on environment
    worker_prefetch_multiplier=1,
)

# Configure periodic tasks (Celery Beat)
celery_app.conf.beat_schedule = {
    'daily-health-recalculation': {
        'task': 'app.workers.analytics_worker.recalculate_enterprise_health',
        'schedule': crontab(hour=0, minute=0), # Every midnight UTC
    },
}
