
"""
Celery application configuration
"""
from celery import Celery
from app.core.config import settings

# Create Celery instance
celery_app = Celery(
    "clipmaster",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.video_tasks",
        "app.tasks.ai_tasks", 
        "app.tasks.twitch_tasks",
        "app.tasks.cleanup_tasks"
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    task_soft_time_limit=3300,  # 55 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    result_expires=3600,
    
    # Task routing
    task_routes={
        "app.tasks.video_tasks.*": {"queue": "video_processing"},
        "app.tasks.ai_tasks.*": {"queue": "ai_processing"},
        "app.tasks.twitch_tasks.*": {"queue": "twitch_monitoring"},
        "app.tasks.cleanup_tasks.*": {"queue": "maintenance"}
    },
    
    # Worker configuration
    worker_redirect_stdouts_level="INFO",
    worker_hijack_root_logger=False,
    
    # Beat schedule for periodic tasks
    beat_schedule={
        "cleanup-temp-files": {
            "task": "app.tasks.cleanup_tasks.cleanup_temp_files",
            "schedule": 3600.0,  # Every hour
        },
        "storage-monitoring": {
            "task": "app.tasks.cleanup_tasks.monitor_storage",
            "schedule": 300.0,  # Every 5 minutes
        },
        "update-stream-status": {
            "task": "app.tasks.twitch_tasks.update_stream_status",
            "schedule": 60.0,  # Every minute
        }
    }
)

if __name__ == "__main__":
    celery_app.start()
