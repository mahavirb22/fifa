"""Crowd intelligence endpoints — density analysis and heatmap data.

Pure computation endpoints — not rate-limited because they use no
external services. The crowd simulator is deterministic and fast.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.crowd.simulator import analyze_crowd, generate_demo_snapshot
from app.models import CrowdAnalysis, CrowdSnapshot

router = APIRouter(prefix="/api/crowd", tags=["crowd"])


@router.get("/density", response_model=CrowdAnalysis)
async def get_crowd_density() -> CrowdAnalysis:
    """Return current crowd density analysis using demo data.

    In production, this would consume real sensor data. For the demo,
    it generates a deterministic pseudo-random snapshot that updates
    every minute to simulate live crowd flow.
    """
    snapshot = generate_demo_snapshot()
    return analyze_crowd(snapshot)


@router.post("/snapshot", response_model=CrowdAnalysis)
async def submit_crowd_snapshot(snapshot: CrowdSnapshot) -> CrowdAnalysis:
    """Analyze a submitted crowd snapshot.

    Accepts zone occupancy data and returns density analysis with
    hotspot identification and overall metrics.
    """
    return analyze_crowd(snapshot)
