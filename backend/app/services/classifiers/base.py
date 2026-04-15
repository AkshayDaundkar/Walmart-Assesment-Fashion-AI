from typing import Protocol

from app.schemas.library import AiAttributes


class ImageClassifier(Protocol):
    def classify_image(self, *, image_bytes: bytes, filename: str) -> tuple[str, AiAttributes]: ...

    def next_id(self) -> str: ...
