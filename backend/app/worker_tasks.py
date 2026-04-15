import logging

from app.core.config import settings
from app.services.classification_runner import execute_classification
from app.storage.factory import get_object_storage

logger = logging.getLogger(__name__)


async def classify_uploaded_item(_ctx: dict[object, object], item_id: str, original_filename: str, object_name: str) -> None:
    _ = _ctx
    if not settings.redis_url:
        logger.error("redis_url is not configured")
        return

    storage = get_object_storage()
    file_bytes = storage.get(object_name=object_name)
    execute_classification(item_id, file_bytes, original_filename)
