def main() -> None:
    import uvicorn

    # Our middleware writes the request log; uvicorn's access log would duplicate it, and its
    # log config would print plain text instead of JSON.
    uvicorn.run("culinary_blog.main:app", host="0.0.0.0", port=8000, reload=True, access_log=False, log_config=None)
