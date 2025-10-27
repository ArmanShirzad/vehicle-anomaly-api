"""Telemetry ingestion endpoint for training isolation forest models."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.domain import ModelTrainingResponse, TelemetryBatch
from app.services.scoring import IsolationForestScoringService, get_scoring_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/ingest", response_model=ModelTrainingResponse, status_code=status.HTTP_201_CREATED)
async def ingest_telemetry(
    batch: TelemetryBatch, service: IsolationForestScoringService = Depends(get_scoring_service)
) -> ModelTrainingResponse:
    """Train or update the anomaly detection model with a batch of telemetry data."""

    try:
        result = service.train(batch)
    except ValueError as exc:  # pragma: no cover - defensive guard
        logger.warning("Telemetry batch rejected: %s", exc)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    logger.info("Telemetry ingestion completed for version %s", result.model_version)
    return result

