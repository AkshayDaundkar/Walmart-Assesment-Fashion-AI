from pathlib import Path

from app.core.config import settings


class LocalObjectStorage:
    def put(self, *, data: bytes, object_name: str, content_type: str | None = None) -> str:
        _ = content_type
        settings.uploads_dir.mkdir(parents=True, exist_ok=True)
        path = settings.uploads_dir / object_name
        path.write_bytes(data)
        return f"{settings.public_assets_base_url.rstrip('/')}/static/uploads/{object_name}"

    def get(self, *, object_name: str) -> bytes:
        path = settings.uploads_dir / object_name
        return path.read_bytes()
