import pytest

from culinary_blog.categories.slug import slugify


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Món Chính", "mon-chinh"),
        ("Đồ uống", "do-uong"),
        ("  Salads & Sides!  ", "salads-sides"),
        ("Desserts", "desserts"),
        ("!!!", ""),
    ],
)
def test_slugify(text, expected):
    assert slugify(text) == expected
