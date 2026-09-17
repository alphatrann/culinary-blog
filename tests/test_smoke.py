def test_app_imports_without_live_dependencies():
    """Settings all have local defaults, so the app must import with no services running."""
    from culinary_blog.main import app

    assert app.title == "Culinary Blog API"
