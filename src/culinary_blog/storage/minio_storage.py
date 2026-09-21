import asyncio
import io
import json
import uuid
from urllib.parse import urlparse

from minio import Minio
from minio.error import S3Error
from urllib3.exceptions import HTTPError

from culinary_blog.config import Settings
from culinary_blog.errors import ServiceUnavailableError
from culinary_blog.storage.service import FileStorageService


class MinioFileStorage(FileStorageService):
    """MinIO implementation. The sync client runs in a worker thread so it never blocks the event loop."""

    def __init__(self, settings: Settings) -> None:
        self._bucket = settings.minio_bucket_name
        scheme = "https" if settings.minio_secure else "http"
        self._prefix = f"{scheme}://{settings.minio_endpoint}/{self._bucket}/"
        self._client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )
        self._bucket_ready = False

    async def upload(self, data: bytes, folder: str, extension: str, content_type: str) -> str:
        key = f"{folder.strip('/')}/{uuid.uuid4()}{extension}"
        await self._run(self._put, key, data, content_type)
        return self._prefix + key

    async def download(self, url: str) -> bytes:
        return await self._run(self._get, self._key_from_url(url))

    async def delete(self, url: str) -> None:
        await self._run(self._remove, self._key_from_url(url))

    def _key_from_url(self, url: str) -> str:
        if not url.startswith(self._prefix):
            raise ValueError(f"URL does not belong to bucket {self._bucket}: {url}")
        return urlparse(url).path.removeprefix(f"/{self._bucket}/")

    def _ensure_bucket(self) -> None:
        if self._bucket_ready:
            return
        if not self._client.bucket_exists(self._bucket):
            self._client.make_bucket(self._bucket)
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": ["*"]},
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{self._bucket}/*"],
                }
            ],
        }
        self._client.set_bucket_policy(self._bucket, json.dumps(policy))  # public-read (FR-FILE-001)
        self._bucket_ready = True

    def _put(self, key: str, data: bytes, content_type: str) -> None:
        self._ensure_bucket()
        self._client.put_object(self._bucket, key, io.BytesIO(data), len(data), content_type=content_type)

    def _get(self, key: str) -> bytes:
        response = self._client.get_object(self._bucket, key)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()

    def _remove(self, key: str) -> None:
        try:
            self._client.remove_object(self._bucket, key)
        except S3Error as exc:
            if exc.code not in {"NoSuchKey", "NoSuchBucket"}:
                raise

    @staticmethod
    async def _run(func, *args):
        try:
            return await asyncio.to_thread(func, *args)
        except (S3Error, HTTPError, OSError) as exc:
            raise ServiceUnavailableError("Dịch vụ lưu trữ tệp tạm thời không khả dụng.") from exc
