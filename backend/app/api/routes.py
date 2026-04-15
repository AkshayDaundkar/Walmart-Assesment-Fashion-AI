"""HTTP surface for library listing, multipart upload, polling, and designer annotation updates."""

from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Query, UploadFile, status

from app.api.deps import get_library_service, get_object_storage_dep
from app.core.config import settings
from app.schemas.library import (
    InspirationImage,
    LibraryResponse,
    UpdateAnnotationsRequest,
    UpdateAnnotationsResponse,
    UploadImageResponse,
)
from app.services.classification_attributes import pending_stub_attributes
from app.services.classification_runner import execute_classification
from app.services.classifier_service import get_image_classifier
from app.services.library_service import LibraryService
from app.storage.base import ObjectStorage

router = APIRouter(prefix="/v1", tags=["library"])


@router.get("/library", response_model=LibraryResponse)
def list_library(
    q: str | None = Query(default=None, description="Natural-language search query"),
    garment_type: str | None = Query(default=None),
    style: str | None = Query(default=None),
    material: str | None = Query(default=None),
    occasion: str | None = Query(default=None),
    consumer_profile: str | None = Query(default=None),
    continent: str | None = Query(default=None),
    country: str | None = Query(default=None),
    city: str | None = Query(default=None),
    time_season: str | None = Query(default=None),
    year: int | None = Query(default=None),
    month: int | None = Query(default=None),
    pattern: str | None = Query(default=None),
    garment_season: str | None = Query(default=None),
    color_palette: str | None = Query(default=None),
    trend_notes: str | None = Query(default=None),
    service: LibraryService = Depends(get_library_service),
) -> LibraryResponse:
    return service.get_library(
        query=q,
        garment_type=garment_type,
        style=style,
        material=material,
        occasion=occasion,
        consumer_profile=consumer_profile,
        continent=continent,
        country=country,
        city=city,
        time_season=time_season,
        year=year,
        month=month,
        pattern=pattern,
        garment_season=garment_season,
        color_palette=color_palette,
        trend_notes=trend_notes,
    )


@router.get("/library/{item_id}", response_model=InspirationImage)
def get_library_item(
    item_id: str,
    service: LibraryService = Depends(get_library_service),
) -> InspirationImage:
    item = service.get_item(item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    return item


@router.post("/library/upload", response_model=UploadImageResponse)
async def upload_and_classify(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    designer_tags: str = Form(default=""),
    designer_notes: str = Form(default=""),
    service: LibraryService = Depends(get_library_service),
    storage: ObjectStorage = Depends(get_object_storage_dep),
) -> UploadImageResponse:
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")

    classifier = get_image_classifier()
    item_id = classifier.next_id()
    safe_filename = file.filename or "upload.jpg"
    extension = Path(safe_filename).suffix or ".jpg"
    object_name = f"{item_id}{extension.lower()}"
    image_url = storage.put(data=file_bytes, object_name=object_name, content_type=file.content_type)

    designer_tag_list = [tag.strip() for tag in designer_tags.split(",") if tag.strip()]
    designer_note_value = designer_notes.strip()
    created_at = datetime.now(UTC).isoformat()

    execution = settings.classification_execution
    if execution == "sync":
        description, attributes = classifier.classify_image(image_bytes=file_bytes, filename=safe_filename)
        item = InspirationImage(
            id=item_id,
            image_url=image_url,
            ai_description=description,
            attributes=attributes,
            designer_tags=designer_tag_list,
            designer_notes=designer_note_value,
            created_at=created_at,
            classification_status="completed",
            classification_error=None,
        )
        return UploadImageResponse(item=service.add_item(item))

    if execution == "background":
        stub = pending_stub_attributes()
        item = InspirationImage(
            id=item_id,
            image_url=image_url,
            ai_description="Classification pending.",
            attributes=stub,
            designer_tags=designer_tag_list,
            designer_notes=designer_note_value,
            created_at=created_at,
            classification_status="pending",
            classification_error=None,
        )
        created = service.add_item(item)
        background_tasks.add_task(execute_classification, item_id, file_bytes, safe_filename)
        return UploadImageResponse(item=created)

    if execution == "arq":
        from arq import create_pool
        from arq.connections import RedisSettings

        if not settings.redis_url:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="redis_url must be set for classification_execution=arq",
            )
        stub = pending_stub_attributes()
        item = InspirationImage(
            id=item_id,
            image_url=image_url,
            ai_description="Classification pending.",
            attributes=stub,
            designer_tags=designer_tag_list,
            designer_notes=designer_note_value,
            created_at=created_at,
            classification_status="pending",
            classification_error=None,
        )
        created = service.add_item(item)
        redis_settings = RedisSettings.from_dsn(settings.redis_url)
        pool = await create_pool(redis_settings)
        try:
            await pool.enqueue_job("classify_uploaded_item", item_id, safe_filename, object_name)
        finally:
            await pool.close()
        return UploadImageResponse(item=created)

    raise HTTPException(status_code=500, detail="Invalid classification_execution")


@router.patch("/library/{item_id}/annotations", response_model=UpdateAnnotationsResponse)
def update_annotations(
    item_id: str,
    payload: UpdateAnnotationsRequest,
    service: LibraryService = Depends(get_library_service),
) -> UpdateAnnotationsResponse:
    updated = service.update_annotations(
        item_id=item_id,
        designer_tags=payload.designer_tags,
        designer_notes=payload.designer_notes,
    )
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    return UpdateAnnotationsResponse(item=updated)
