from app.repositories.library_repository import LibraryRepository
from app.services.library_service import LibraryService
from app.storage.base import ObjectStorage
from app.storage.factory import get_object_storage

_repository: LibraryRepository | None = None


def get_library_repository() -> LibraryRepository:
    global _repository
    if _repository is None:
        _repository = LibraryRepository()
    return _repository


def get_library_service() -> LibraryService:
    return LibraryService(repository=get_library_repository())


def get_object_storage_dep() -> ObjectStorage:
    return get_object_storage()
