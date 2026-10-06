"""Dump the FastAPI OpenAPI schema to `web/openapi.json` (input for `npm run api:types`)."""

import json
import sys
from pathlib import Path

from culinary_blog.main import app

TARGET = Path(__file__).resolve().parent.parent / "web" / "openapi.json"


def main() -> int:
    TARGET.write_text(json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n")
    print(f"wrote {TARGET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
