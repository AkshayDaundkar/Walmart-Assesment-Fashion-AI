from arq.connections import RedisSettings

from app.core.config import settings
from app.worker_tasks import classify_uploaded_item


class WorkerSettings:
    functions = [classify_uploaded_item]
    redis_settings = RedisSettings.from_dsn(settings.redis_url or "redis://localhost:6379")
    job_timeout = 600
