import pytest


def test_app_imports_without_live_dependencies():
    """Settings all have local defaults, so the app must import with no services running."""
    from culinary_blog.main import app

    assert app.title == "Culinary Blog API"


@pytest.mark.parametrize("field", ["jwt_secret_key", "ratelimit_hash_key"])
def test_dev_only_secrets_rejected_outside_development(field: str) -> None:
    from culinary_blog.config import Settings

    secrets = {"jwt_secret_key": "real-jwt", "ratelimit_hash_key": "real-hash"}
    secrets.pop(field)
    with pytest.raises(ValueError, match=field.upper()):
        Settings(environment="production", _env_file=None, **secrets)
