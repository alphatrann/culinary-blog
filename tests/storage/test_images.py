import pytest

from culinary_blog.errors import BadRequestError
from culinary_blog.storage.images import AVIF, JPEG, MAX_IMAGE_BYTES, PNG, WEBP, sniff_image_format, validate_image


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (b"\xff\xd8\xff\xdb" + b"0" * 20, JPEG),
        (b"\x89PNG\r\n\x1a\n" + b"0" * 20, PNG),
        (b"RIFF1234WEBPVP8 ", WEBP),
        (b"\x00\x00\x00\x20ftypavis", AVIF),
        (b"GIF89a" + b"0" * 20, None),
        (b"", None),
    ],
)
def test_sniff_image_format(data, expected):
    assert sniff_image_format(data) == expected


def test_validate_returns_detected_format():
    assert validate_image("image/png", b"\x89PNG\r\n\x1a\n" + b"0" * 8) == PNG


def test_validate_accepts_exactly_max_size():
    assert validate_image("image/jpeg", b"\xff\xd8\xff" + b"0" * (MAX_IMAGE_BYTES - 3)) == JPEG


def test_validate_rejects_one_byte_over_max():
    with pytest.raises(BadRequestError):
        validate_image("image/jpeg", b"\xff\xd8\xff" + b"0" * (MAX_IMAGE_BYTES - 2))


@pytest.mark.parametrize("content_type", [None, "", "image/svg+xml", "application/octet-stream"])
def test_validate_rejects_unsupported_content_type(content_type):
    with pytest.raises(BadRequestError):
        validate_image(content_type, b"\xff\xd8\xff" + b"0" * 8)
