"""Synchronous classification job: read bytes from storage caller, classify, then persist or mark failed."""

import logging

from app.repositories.library_repository import LibraryRepository
from app.services.classification_attributes import pending_stub_attributes
from app.services.classifier_service import get_image_classifier

logger = logging.getLogger(__name__)


def execute_classification(item_id: str, file_bytes: bytes, filename: str) -> None:
    repository = LibraryRepository()
    classifier = get_image_classifier()
    try:
        description, attributes = classifier.classify_image(image_bytes=file_bytes, filename=filename)
        repository.update_classification(
            item_id,
            ai_description=description,
            attributes_json=attributes.model_dump_json(),
            status="completed",
            error=None,
        )
    except Exception as exc:
        logger.exception("Classification failed for item %s", item_id)
        stub = pending_stub_attributes()
        repository.update_classification(
            item_id,
            ai_description="Classification failed.",
            attributes_json=stub.model_dump_json(),
            status="failed",
            error=str(exc),
        )
