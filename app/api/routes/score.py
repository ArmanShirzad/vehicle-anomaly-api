"""Anomaly scoring endpoint for telemetry records."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.domain import ScoreRequest, ScoreResponse
from app.services.scoring import IsolationForestScoringService, get_scoring_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/score", response_model=ScoreResponse, status_code=status.HTTP_200_OK)
async def score_telemetry(
    request: ScoreRequest, service: IsolationForestScoringService = Depends(get_scoring_service)
) -> ScoreResponse:
    """Score a telemetry record for anomalies using the configured isolation forest model."""

    try:
        response = service.score(request)
    except FileNotFoundError as exc:
        logger.error("Model version not available: %s", exc)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (TypeError, ValueError) as exc:  # pragma: no cover - defensive guard
        logger.exception("Failed to score telemetry")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    logger.info(
        "Telemetry scored for vehicle %s with version %s",
        response.vehicle_id,
        response.model_version,
    )
    return response

