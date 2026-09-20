import re
import unicodedata


def slugify(text: str) -> str:
    """Lowercase, accent-free, hyphen-separated ("Món Chính" -> "mon-chinh"). Empty if nothing usable remains."""
    text = text.replace("đ", "d").replace("Đ", "D")
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
