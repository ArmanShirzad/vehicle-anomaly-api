"""OpenTelemetry instrumentation setup for the FastAPI application."""

from __future__ import annotations

import os
import threading
from typing import Final

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.config import settings

_INITIALISED_LOCK: Final = threading.Lock()
_INITIALISED: bool = False


def init_tracing(app: FastAPI) -> None:
    """Initialise OpenTelemetry tracing for the FastAPI app."""

    global _INITIALISED
    if _INITIALISED:
        return

    with _INITIALISED_LOCK:
        if _INITIALISED:
            return

        endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
        insecure = os.getenv("OTEL_EXPORTER_OTLP_INSECURE", "true").lower() == "true"

        resource = Resource.create(
            {
                "service.name": settings.app_name,
                "service.version": settings.app_version,
                "deployment.environment": settings.environment,
            }
        )

        tracer_provider = TracerProvider(resource=resource)
        span_processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint, insecure=insecure))
        tracer_provider.add_span_processor(span_processor)
        trace.set_tracer_provider(tracer_provider)

        FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer_provider)

        _INITIALISED = True

