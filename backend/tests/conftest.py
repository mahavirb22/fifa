"""Shared test fixtures — client, env overrides, cache clearing."""

import os

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def _env_overrides(monkeypatch):
    """Override environment to disable cloud services in tests."""
    monkeypatch.setenv("USE_GEMINI", "false")
    monkeypatch.setenv("USE_FIRESTORE", "false")
    monkeypatch.setenv("GCP_PROJECT_ID", "test-project")
    monkeypatch.setenv("GCP_REGION", "us-central1")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:5173")


@pytest.fixture(autouse=True)
def _clear_caches():
    """Clear lru_cache singletons between tests."""
    from app.config import get_settings
    from app.deps import get_repository
    from app.advisor.gemini import _get_gemini_client

    get_settings.cache_clear()
    get_repository.cache_clear()
    _get_gemini_client.cache_clear()
    yield
    get_settings.cache_clear()
    get_repository.cache_clear()
    _get_gemini_client.cache_clear()


@pytest.fixture()
def client():
    """Create a fresh TestClient for each test."""
    from app.main import create_app

    app = create_app()
    with TestClient(app) as tc:
        yield tc
