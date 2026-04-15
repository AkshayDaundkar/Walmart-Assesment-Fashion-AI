from app.core.config import settings
from app.storage.base import ObjectStorage
from app.storage.local_storage import LocalObjectStorage


def get_object_storage() -> ObjectStorage:
    match settings.storage_backend:
        case "local":
            return LocalObjectStorage()
        case "s3":
            from app.storage.s3_storage import S3ObjectStorage

            return S3ObjectStorage()
