import asyncio
import logging
import os
import socket
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry import metrics, trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.metrics import CallbackOptions, Observation
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from culinary_blog.auth.wiring import build_auth_router
from culinary_blog.categories.wiring import build_categories_router
from culinary_blog.config import get_settings
from culinary_blog.database.session import DB_MAX_OVERFLOW, DB_POOL_SIZE, engine
from culinary_blog.health.wiring import build_health_router
from culinary_blog.logging import configure_logging
from culinary_blog.middleware import CorrelationIdMiddleware
from culinary_blog.problem_details import register_problem_handlers
from culinary_blog.ratelimit.wiring import api_rate_limit, auth_rate_limit
from culinary_blog.recipes.wiring import build_recipes_router

settings = get_settings()
configure_logging()

# Tempo traces under M6a load showed multi-hundred-ms gaps between spans that no
# application code accounts for (ADR-0009) - the coroutine was simply queued,
# waiting its turn on the single uvicorn worker. A span can't cover a gap where
# nothing runs, so this polls how long a no-op `asyncio.sleep(0)` actually takes:
# a direct signal of event-loop scheduling delay/saturation, surfaced as a metric.
_event_loop_lag_seconds = 0.0


def _read_event_loop_lag(_options: CallbackOptions) -> list[Observation]:
    return [Observation(_event_loop_lag_seconds)]


async def _measure_event_loop_lag() -> None:
    global _event_loop_lag_seconds
    while True:
        start = time.monotonic()
        await asyncio.sleep(0)
        _event_loop_lag_seconds = time.monotonic() - start
        await asyncio.sleep(1)


# The undersized default pool (5 + 10 overflow) meant requests queued above asyncpg
# waiting for a free connection - a gap no span covers, since checkout happens before
# asyncpg's own instrumented calls even start (ADR-0009). Exposed directly so
# saturation is visible instead of showing up only as an unexplained trace gap.
_db_pool_capacity = DB_POOL_SIZE + DB_MAX_OVERFLOW


def _read_db_pool_checked_out(_options: CallbackOptions) -> list[Observation]:
    return [Observation(engine.pool.checkedout())]


def _read_db_pool_capacity(_options: CallbackOptions) -> list[Observation]:
    return [Observation(_db_pool_capacity)]


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    task = asyncio.create_task(_measure_event_loop_lag())
    try:
        yield
    finally:
        task.cancel()


app = FastAPI(title="Culinary Blog API", version="0.1.0", lifespan=lifespan)

# RED metrics + traces for the M6a/M6b load-test dashboards (ADR-0009). Logs are JSON on stdout
# (configure_logging, CONS-010) and also OTLP when otel_enabled.
# One series per uvicorn worker: without a distinct instance id every worker exports the same counter identity and
# the collector's Prometheus exporter keeps only one of them (the cache hit-rate counters would undercount).
resource = Resource.create(
    {"service.name": settings.otel_service_name, "service.instance.id": f"{socket.gethostname()}-{os.getpid()}"}
)

trace.set_tracer_provider(TracerProvider(resource=resource))
if settings.otel_enabled:
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint, insecure=True))
    )
metrics.set_meter_provider(
    MeterProvider(
        resource=resource,
        metric_readers=[
            PeriodicExportingMetricReader(
                OTLPMetricExporter(endpoint=settings.otel_exporter_otlp_endpoint, insecure=True)
            )
        ]
        if settings.otel_enabled
        else [],
    )
)
if settings.otel_enabled:
    # The collector's logs pipeline only accepts OTLP, so stdout JSON alone never reaches Loki (observability/).
    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(OTLPLogExporter(endpoint=settings.otel_exporter_otlp_endpoint, insecure=True))
    )
    set_logger_provider(logger_provider)
    otel_log_handler = LoggingHandler(logger_provider=logger_provider)
    # Drop the SDK's own logs (exporter failures) so they can't feed back into the pipeline.
    otel_log_handler.addFilter(lambda record: not record.name.startswith("opentelemetry"))
    logging.getLogger().addHandler(otel_log_handler)

_meter = metrics.get_meter(__name__)
_meter.create_observable_gauge(
    "asyncio_event_loop_lag_seconds",
    callbacks=[_read_event_loop_lag],
    description="Delay of a no-op asyncio.sleep(0); a direct signal of event-loop scheduling saturation.",
    unit="s",
)
_meter.create_observable_gauge(
    "db_pool_checked_out_connections",
    callbacks=[_read_db_pool_checked_out],
    description="SQLAlchemy pool connections currently checked out; compare to db_pool_capacity for saturation.",
)
_meter.create_observable_gauge(
    "db_pool_capacity",
    callbacks=[_read_db_pool_capacity],
    description="Configured pool_size + max_overflow (NFR-SCALE-002 budget).",
)
FastAPIInstrumentor.instrument_app(app)
AsyncPGInstrumentor().instrument()

register_problem_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "If-Match", "X-Correlation-ID"],
    expose_headers=[
        "Retry-After",
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
        "X-RateLimit-Reset",
        "X-Correlation-ID",
    ],
)
# Added last so it is outermost: CORS preflights get a correlation id and a request log too.
app.add_middleware(CorrelationIdMiddleware)

app.include_router(build_health_router())
app.include_router(build_auth_router(), dependencies=[Depends(auth_rate_limit())])
app.include_router(build_categories_router(), dependencies=[Depends(api_rate_limit())])
app.include_router(build_recipes_router(), dependencies=[Depends(api_rate_limit())])
