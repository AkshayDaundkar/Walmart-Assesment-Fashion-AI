"""FastAPI application: CORS, request IDs, DB init, optional demo seed, and library routes."""

import logging
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.deps import get_library_repository
from app.api.routes import router
from app.core.config import settings
from app.db.init_db import initialize_database
from app.schemas.library import InspirationImage
from app.services.classifier_service import get_image_classifier
from app.services.library_service import LibraryService


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    initialize_database()

    if settings.seed_demo_data:
        repository = get_library_repository()
        if not repository.list_items():
            classifier = get_image_classifier()
            demo_id = classifier.next_id()
            description, attributes = classifier.classify_image(
                image_bytes=b"",
                filename="seed_jaipur_ethnic_top.jpg",
            )
            demo = InspirationImage(
                id=demo_id,
                image_url="https://images.pexels.com/photos/5325886/pexels-photo-5325886.jpeg",
                ai_description=description,
                attributes=attributes,
                designer_tags=["neckline", "embroidery"],
                designer_notes="Seed record for local development",
                created_at="2026-03-09T10:00:00Z",
                classification_status="completed",
                classification_error=None,
            )
            LibraryService(repository=repository).add_item(demo)

    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(RequestIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

storage_dir = settings.uploads_dir.parent
storage_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=storage_dir), name="static")

app.include_router(router)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
