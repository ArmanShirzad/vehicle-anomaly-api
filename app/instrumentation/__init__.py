"""Instrumentation utilities for the FastAPI application."""

from .otel import init_tracing

__all__ = ["init_tracing"]

