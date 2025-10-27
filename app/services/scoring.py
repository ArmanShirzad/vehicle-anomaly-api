"""Isolation Forest scoring and model management service."""

from __future__ import annotations

import logging
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest

from app.config import settings
from app.domain import (
    IsolationForestMetadata,
    ModelTrainingResponse,
    ScoreRequest,
    ScoreResponse,
    TelemetryBatch,
    TelemetryRecord,
)

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class IsolationForestConfig:
    """Configuration options for the IsolationForest model."""

    n_estimators: int = 200
    contamination: float = 0.05
    random_state: int = 42


class IsolationForestScoringService:
    """Service responsible for training and scoring telemetry data."""

    def __init__(self, artifact_dir: str | Path, config: IsolationForestConfig | None = None):
        self.artifact_dir = Path(artifact_dir)
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        self.latest_file = self.artifact_dir / "LATEST"
        self.config = config or IsolationForestConfig()

    # ------------------------------------------------------------------
    # Artifact helpers
    # ------------------------------------------------------------------
    def _model_path(self, version: str) -> Path:
        return self.artifact_dir / f"isolation_forest_{version}.joblib"

    def _metadata_path(self, version: str) -> Path:
        return self.artifact_dir / f"isolation_forest_{version}.metadata.json"

    def _write_latest_version(self, version: str) -> None:
        self.latest_file.write_text(version, encoding="utf-8")

    def _read_latest_version(self) -> str:
        if not self.latest_file.exists():
            msg = "No trained model available"
            raise FileNotFoundError(msg)
        return self.latest_file.read_text(encoding="utf-8").strip()

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------
    def train(self, batch: TelemetryBatch) -> ModelTrainingResponse:
        """Train an IsolationForest model using a batch of telemetry records."""

        feature_matrix = self._to_matrix(batch.records)
        if feature_matrix.size == 0:
            msg = "Telemetry batch must contain records"
            raise ValueError(msg)

        model_version = batch.model_version or datetime.now(tz=UTC).strftime("%Y%m%d%H%M%S")
        model = IsolationForest(
            n_estimators=self.config.n_estimators,
            contamination=self.config.contamination,
            random_state=self.config.random_state,
        )
        model.fit(feature_matrix)

        artifact_path = self._model_path(model_version)
        joblib.dump(model, artifact_path)
        logger.info("IsolationForest model persisted at %s", artifact_path)

        metadata = IsolationForestMetadata(
            model_version=model_version,
            trained_at=datetime.now(tz=UTC),
            n_estimators=self.config.n_estimators,
            contamination=self.config.contamination,
            n_features=feature_matrix.shape[1],
        )
        joblib.dump(metadata.model_dump(), self._metadata_path(model_version))
        logger.debug("Metadata persisted for model version %s", model_version)

        self._write_latest_version(model_version)
        logger.info("Updated latest model pointer to version %s", model_version)

        return ModelTrainingResponse(
            model_version=model_version,
            record_count=len(batch.records),
            metadata=metadata,
        )

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------
    def score(self, request: ScoreRequest) -> ScoreResponse:
        """Score a single telemetry record using the requested model version."""

        model_version = request.model_version or self._read_latest_version()
        model = self._load_model(model_version)

        feature_vector = np.array(request.feature_vector, dtype=float).reshape(1, -1)
        anomaly_score = float(model.decision_function(feature_vector)[0])
        is_anomaly = bool(model.predict(feature_vector)[0] == -1)

        return ScoreResponse(
            vehicle_id=request.vehicle_id,
            timestamp=request.timestamp,
            model_version=model_version,
            anomaly_score=anomaly_score,
            is_anomaly=is_anomaly,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _load_model(self, version: str) -> IsolationForest:
        path = self._model_path(version)
        if not path.exists():
            msg = f"Model version '{version}' is not available"
            raise FileNotFoundError(msg)
        model = joblib.load(path)
        if not isinstance(model, IsolationForest):
            msg = f"Artifact at {path} is not an IsolationForest model"
            raise TypeError(msg)
        return model

    @staticmethod
    def _to_matrix(records: Iterable[TelemetryRecord]) -> np.ndarray:
        return np.array([record.feature_vector for record in records], dtype=float)


_service_instance: IsolationForestScoringService | None = None


def get_scoring_service() -> IsolationForestScoringService:
    """Return a singleton scoring service instance."""

    global _service_instance
    if _service_instance is None:
        _service_instance = IsolationForestScoringService(settings.model_artifact_dir)
    return _service_instance


def reset_scoring_service() -> None:
    """Reset the cached scoring service instance (useful for tests)."""

    global _service_instance
    _service_instance = None

