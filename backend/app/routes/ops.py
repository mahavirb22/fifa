"""Operations endpoints — AI recommendations and action logging.

The recommendations endpoint is rate-limited because it may invoke Gemini.
The action logging endpoint is not rate-limited — staff need to log actions
without delay during critical situations.
"""

from fastapi import APIRouter, Depends, Request

from app.advisor.gemini import get_ops_recommendations
from app.config import Settings, get_settings
from app.crowd.simulator import analyze_crowd, generate_demo_snapshot
from app.deps import get_repository
from app.models import OpsActionRecord, OpsActionRequest, OpsRecommendation
from app.rate_limit import limiter
from app.repository.base import OpsRepository

router = APIRouter(prefix="/api/ops", tags=["operations"])


@router.get("/recommendations", response_model=list[OpsRecommendation])
@limiter.limit("10/minute")
async def get_recommendations(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> list[OpsRecommendation]:
    """Get AI-powered operational recommendations based on current crowd state.

    Analyzes live crowd density and generates actionable recommendations
    for venue staff. Uses Gemini when available, rules engine as fallback.
    """
    snapshot = generate_demo_snapshot()
    analysis = analyze_crowd(snapshot)

    return await get_ops_recommendations(
        analysis=analysis,
        use_gemini=settings.use_gemini,
        project=settings.gcp_project_id,
        region=settings.gcp_region,
        prompt_version=settings.gemini_prompt_version,
    )


@router.post("/action", response_model=OpsActionRecord)
async def log_action(
    body: OpsActionRequest,
    repo: OpsRepository = Depends(get_repository),
) -> OpsActionRecord:
    """Log an operational action taken by staff.

    Persists the action record for audit trail and trend analysis.
    Not rate-limited — staff need immediate response during incidents.
    """
    return await repo.async_log_action(body)


@router.get("/actions", response_model=list[OpsActionRecord])
async def list_actions(
    repo: OpsRepository = Depends(get_repository),
) -> list[OpsActionRecord]:
    """List recent operational actions, newest first."""
    return await repo.async_list_actions(limit=50)
