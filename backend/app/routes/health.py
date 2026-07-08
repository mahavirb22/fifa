"""Health check endpoint — service status and dependency availability."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app import __version__
from app.config import Settings, get_settings
from app.models import HealthStatus

router = APIRouter(tags=["health"])


@router.get("/api/health", response_model=HealthStatus)
async def health_check(
    settings: Settings = Depends(get_settings),
) -> HealthStatus:
    """Return service health including dependency availability.

    Reports whether Gemini and Firestore are configured (not whether
    they are reachable — that would add latency to the health check).
    """
    return HealthStatus(
        status="healthy" if not settings.use_gemini or settings.gcp_project_id else "degraded",
        version=__version__,
        gemini_available=settings.use_gemini,
        firestore_available=settings.use_firestore,
    )
