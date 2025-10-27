"""Prometheus metrics setup."""

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import settings


def setup_metrics(app: FastAPI) -> None:
    """Setup Prometheus metrics instrumentation."""
    Instrumentator().instrument(app).expose(app)

