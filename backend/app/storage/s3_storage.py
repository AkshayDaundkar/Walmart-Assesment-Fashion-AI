import mimetypes
from pathlib import Path
from uuid import uuid4

import boto3
from botocore.client import BaseClient

from app.core.config import settings


class S3ObjectStorage:
    def __init__(self) -> None:
        if not settings.s3_bucket:
            msg = "s3_bucket must be set when storage_backend is s3"
            raise ValueError(msg)
        session = boto3.session.Session(
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.s3_region,
        )
        self._client: BaseClient = session.client("s3", endpoint_url=settings.s3_endpoint_url)
        self._bucket = settings.s3_bucket

    def put(self, *, data: bytes, object_name: str, content_type: str | None = None) -> str:
        key = f"{settings.s3_key_prefix.strip('/')}/{object_name}"
        extra: dict[str, str] = {}
        if content_type:
            extra["ContentType"] = content_type
        else:
            guessed, _ = mimetypes.guess_type(object_name)
            if guessed:
                extra["ContentType"] = guessed

        self._client.put_object(Bucket=self._bucket, Key=key, Body=data, **extra)

        if settings.s3_endpoint_url:
            base = settings.s3_endpoint_url.rstrip("/")
            return f"{base}/{self._bucket}/{key}"

        region = settings.s3_region or "us-east-1"
        return f"https://{self._bucket}.s3.{region}.amazonaws.com/{key}"

    def get(self, *, object_name: str) -> bytes:
        key = f"{settings.s3_key_prefix.strip('/')}/{object_name}"
        response = self._client.get_object(Bucket=self._bucket, Key=key)
        body = response["Body"].read()
        return body


def unique_object_name(original_name: str) -> str:
    suffix = Path(original_name).suffix or ".jpg"
    return f"{uuid4().hex}{suffix.lower()}"
