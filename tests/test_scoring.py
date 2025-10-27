from __future__ import annotations

from datetime import UTC, datetime

from fastapi.testclient import TestClient


def _sample_batch():
    timestamp = datetime.now(tz=UTC).isoformat()
    return {
        "records": [
            {
                "vehicle_id": "vehicle-1",
                "timestamp": timestamp,
                "feature_vector": [0.1, 0.2, 0.3],
            },
            {
                "vehicle_id": "vehicle-2",
                "timestamp": timestamp,
                "feature_vector": [0.15, 0.22, 0.31],
            },
            {
                "vehicle_id": "vehicle-3",
                "timestamp": timestamp,
                "feature_vector": [0.12, 0.19, 0.29],
            },
        ]
    }


def test_ingest_creates_model(client: TestClient):
    response = client.post("/ingest", json=_sample_batch())
    assert response.status_code == 201
    body = response.json()
    assert body["record_count"] == 3
    assert "model_version" in body
    assert body["metadata"]["n_features"] == 3


def test_score_uses_latest_model_by_default(client: TestClient):
    ingest_response = client.post("/ingest", json=_sample_batch())
    model_version = ingest_response.json()["model_version"]

    telemetry = {
        "vehicle_id": "vehicle-1",
        "timestamp": datetime.now(tz=UTC).isoformat(),
        "feature_vector": [0.13, 0.2, 0.28],
    }

    score_response = client.post("/score", json=telemetry)
    assert score_response.status_code == 200
    body = score_response.json()
    assert body["model_version"] == model_version
    assert isinstance(body["anomaly_score"], float)
    assert isinstance(body["is_anomaly"], bool)


def test_score_specific_version(client: TestClient):
    ingest_response = client.post("/ingest", json=_sample_batch())
    model_version = ingest_response.json()["model_version"]

    telemetry = {
        "vehicle_id": "vehicle-2",
        "timestamp": datetime.now(tz=UTC).isoformat(),
        "feature_vector": [0.16, 0.21, 0.27],
        "model_version": model_version,
    }

    score_response = client.post("/score", json=telemetry)
    assert score_response.status_code == 200
    assert score_response.json()["model_version"] == model_version


def test_score_unknown_version_returns_404(client: TestClient):
    telemetry = {
        "vehicle_id": "vehicle-2",
        "timestamp": datetime.now(tz=UTC).isoformat(),
        "feature_vector": [0.16, 0.21, 0.27],
        "model_version": "non-existent",
    }

    response = client.post("/score", json=telemetry)
    assert response.status_code == 404
    assert "not available" in response.json()["detail"]

