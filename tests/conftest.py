"""Test configuration."""

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.services.scoring import reset_scoring_service


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def sample_item():
    """Sample item data for testing."""
    return {"name": "Test Item", "description": "A test item", "price": 9.99}


@pytest.fixture(autouse=True)
def isolated_artifact_dir(tmp_path, monkeypatch):
    """Ensure model artifacts are written to a temporary directory for each test run."""

    original_dir = settings.model_artifact_dir
    monkeypatch.setattr(settings, "model_artifact_dir", str(tmp_path))
    reset_scoring_service()
    try:
        yield
    finally:
        monkeypatch.setattr(settings, "model_artifact_dir", original_dir)
        reset_scoring_service()

