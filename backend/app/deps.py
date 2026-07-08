"""Dependency injection wiring — selects implementations based on config.

Routes never import concrete implementations directly. They depend on
the Protocol type and receive the correct implementation via Depends().
"""

from __future__ import annotations

from functools import lru_cache

from app.config import Settings, get_settings
from app.repository.base import OpsRepository
from app.repository.memory_repo import MemoryOpsRepository


@lru_cache(maxsize=1)
def get_repository() -> OpsRepository:
    """Return the repository implementation based on USE_FIRESTORE flag."""
    settings = get_settings()
    if settings.use_firestore:
        from app.repository.firestore_repo import FirestoreOpsRepository

        return FirestoreOpsRepository(project_id=settings.gcp_project_id)  # type: ignore[return-value]
    return MemoryOpsRepository()  # type: ignore[return-value]
