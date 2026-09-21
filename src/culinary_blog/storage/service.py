from abc import ABC, abstractmethod


class FileStorageService(ABC):
    """Binary file storage (FR-FILE-001/002). Implementations are swappable (MinIO, S3, local filesystem)."""

    @abstractmethod
    async def upload(self, data: bytes, folder: str, extension: str, content_type: str) -> str:
        """Store `data` as `{folder}/{uuid4()}{extension}` and return its public URL."""

    @abstractmethod
    async def download(self, url: str) -> bytes:
        """Fetch the bytes of a file previously returned by `upload`."""

    @abstractmethod
    async def delete(self, url: str) -> None:
        """Remove a file by URL. Idempotent: a missing object is not an error."""
