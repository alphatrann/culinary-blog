from dataclasses import dataclass

from culinary_blog.errors import BadRequestError

MAX_IMAGE_BYTES = 5 * 1024 * 1024  # CONS-007


@dataclass(frozen=True)
class ImageFormat:
    content_type: str
    extension: str


JPEG = ImageFormat("image/jpeg", ".jpg")
PNG = ImageFormat("image/png", ".png")
WEBP = ImageFormat("image/webp", ".webp")
AVIF = ImageFormat("image/avif", ".avif")
ALLOWED_CONTENT_TYPES = {f.content_type for f in (JPEG, PNG, WEBP, AVIF)}


def sniff_image_format(data: bytes) -> ImageFormat | None:
    """Identify the format from magic bytes, never from the client-supplied name or Content-Type."""
    if data.startswith(b"\xff\xd8\xff"):
        return JPEG
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return PNG
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return WEBP
    if data[4:8] == b"ftyp" and data[8:12] in (b"avif", b"avis"):
        return AVIF
    return None


def validate_image(content_type: str | None, data: bytes) -> ImageFormat:
    """FR-RCP-008 steps 2-3: allowed MIME type, size <= 5 MB, and magic bytes that agree with the MIME type."""
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise BadRequestError("Chỉ chấp nhận ảnh JPEG, PNG, WebP hoặc AVIF.")
    if not data:
        raise BadRequestError("File ảnh rỗng.")
    if len(data) > MAX_IMAGE_BYTES:
        raise BadRequestError("Ảnh vượt quá dung lượng tối đa 5 MB.")
    detected = sniff_image_format(data)
    if detected is None or detected.content_type != content_type:
        raise BadRequestError("Nội dung file không khớp với định dạng ảnh đã khai báo.")
    return detected
