from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from culinary_blog.auth.wiring import build_auth_router
from culinary_blog.config import get_settings
from culinary_blog.health.wiring import build_health_router
from culinary_blog.problem_details import register_problem_handlers

settings = get_settings()

app = FastAPI(title="Culinary Blog API", version="0.1.0")

register_problem_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-Correlation-ID"],
)

app.include_router(build_health_router())
app.include_router(build_auth_router())
