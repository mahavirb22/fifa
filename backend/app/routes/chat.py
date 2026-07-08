"""Fan chat endpoint — multilingual AI assistant for stadium queries.

Rate-limited to 10 requests/minute per IP because each request may
invoke the Gemini API (cost and quota implications).
"""

from fastapi import APIRouter, Depends, Request

from app.advisor.gemini import get_fan_response
from app.config import Settings, get_settings
from app.models import ChatRequest, ChatResponse
from app.rate_limit import limiter

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
@limiter.limit("10/minute")
async def chat_with_assistant(
    request: Request,
    body: ChatRequest,
    settings: Settings = Depends(get_settings),
) -> ChatResponse:
    """Process a fan's query and return an AI-powered response.

    Gemini provides personalized, multilingual responses. When unavailable,
    the rules engine provides template-based responses in 12+ languages.
    """
    return await get_fan_response(
        message=body.message,
        language=body.language,
        device_id=body.device_id,
        use_gemini=settings.use_gemini,
        project=settings.gcp_project_id,
        region=settings.gcp_region,
        prompt_version=settings.gemini_prompt_version,
    )
