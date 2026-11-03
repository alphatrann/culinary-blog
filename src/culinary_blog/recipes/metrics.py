"""Recipe lifecycle counters (FR-OBS-001 custom business metrics), exported over OTLP when otel_enabled."""

from opentelemetry import metrics

_meter = metrics.get_meter(__name__)

recipes_created = _meter.create_counter("recipes_created_total", description="Recipes created, drafts included.")
recipes_published = _meter.create_counter(
    "recipes_published_total", description="Recipes published for the first time (re-publish is a no-op)."
)
