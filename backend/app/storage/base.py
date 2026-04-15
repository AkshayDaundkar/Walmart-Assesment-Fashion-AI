from typing import Protocol


class ObjectStorage(Protocol):
    """Stores binary objects and returns a publicly reachable URL for the client."""

    def put(self, *, data: bytes, object_name: str, content_type: str | None = None) -> str: ...

    def get(self, *, object_name: str) -> bytes: ...
