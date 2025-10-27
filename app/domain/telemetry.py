"""Telemetry domain models for isolation forest scoring."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Self

from pydantic import BaseModel, Field, model_validator


class TelemetryRecord(BaseModel):
    """Represents a single telemetry measurement for a vehicle."""

    vehicle_id: Annotated[str, Field(min_length=1, max_length=64)]
    timestamp: datetime
    feature_vector: Annotated[list[float], Field(min_length=1)]

    @model_validator(mode="after")
    def validate_feature_vector(self) -> Self:
        """Ensure the feature vector is numeric."""
        if not all(isinstance(value, float | int) for value in self.feature_vector):
            msg = "feature_vector must contain only numeric values"
            raise ValueError(msg)
        # Coerce ints to floats to keep downstream numpy happy
        self.feature_vector = [float(value) for value in self.feature_vector]
        return self


class TelemetryBatch(BaseModel):
    """Batch payload used to train or update the isolation forest."""

    records: Annotated[list[TelemetryRecord], Field(min_length=1)]
    model_version: Annotated[str | None, Field(default=None, max_length=128)] = None


class IsolationForestMetadata(BaseModel):
    """Metadata that accompanies a trained isolation forest artifact."""

    model_version: Annotated[str, Field(min_length=1, max_length=128)]
    trained_at: datetime
    n_estimators: int
    contamination: float
    n_features: int


class ModelTrainingResponse(BaseModel):
    """Response returned by the ingestion endpoint after training."""

    model_version: str
    record_count: int
    metadata: IsolationForestMetadata


class ScoreRequest(TelemetryRecord):
    """Request payload for scoring a single telemetry record."""

    model_version: Annotated[str | None, Field(default=None, max_length=128)] = None


class ScoreResponse(BaseModel):
    """Response payload for anomaly scoring."""

    vehicle_id: str
    timestamp: datetime
    model_version: str
    anomaly_score: float
    is_anomaly: bool

