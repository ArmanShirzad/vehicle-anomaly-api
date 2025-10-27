"""Health check endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException

from app.config import settings
from app.core.database import check_database_health

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.environment,
    }


@router.get("/health/ready")
async def readiness_check():
    """Readiness check endpoint that includes database connectivity."""
    db_status = await check_database_health()
    return {
        "status": "ready",
        "version": settings.app_version,
        "environment": settings.environment,
        "database": "connected" if db_status and settings.database_url else "not configured",
    }


@router.get("/healthz")
async def liveness_probe():
    """Kubernetes/ECS-style liveness probe."""
    return {"status": "ok"}

