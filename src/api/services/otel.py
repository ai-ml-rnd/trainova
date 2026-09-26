"""OpenTelemetry instrumentation."""

import logging
import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.langchain import LangchainInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.config import settings

logger = logging.getLogger(__name__)


def init_otel() -> None:
    """Initialize OpenTelemetry."""
    if not settings.otel_enabled:
        logger.info("OTel disabled")
        return

    # Configure resource
    resource = Resource.create({
        "service.name": "forge-api",
        "service.version": settings.app_version,
        "deployment.environment": settings.environment,
    })

    # Configure trace provider
    trace_provider = TracerProvider(resource=resource)

    # Add OTLP exporter
    otlp_exporter = OTLPSpanExporter(
        endpoint=settings.otel_endpoint,
        insecure=not settings.is_production,
    )
    span_processor = BatchSpanProcessor(otlp_exporter)
    trace_provider.add_span_processor(span_processor)

    # Set global trace provider
    trace.set_tracer_provider(trace_provider)

    # Instrument FastAPI
    FastAPIInstrumentor().instrument()

    # Instrument LangChain
    LangchainInstrumentor().instrument()

    logger.info("OTel initialized")


def get_tracer(name: str) -> trace.Tracer:
    """Get a tracer."""
    return trace.get_tracer(name)
