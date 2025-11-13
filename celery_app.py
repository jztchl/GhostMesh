from celery import Celery

from config import settings

celery_client = Celery(
    "celery_app",
    broker=settings.REDIS_CELERY_BROKER,
    backend=settings.REDIS_CELERY_BROKER,
)


celery_client.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    include=["tasks.task_generate_avatar"],
)
celery_client.autodiscover_tasks()
