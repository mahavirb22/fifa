from unittest.mock import MagicMock, patch
import pytest
from app.advisor.gemini import (
    get_fan_response,
    get_ops_recommendations,
    _validate_fan_response,
    _validate_ops_response,
)
from app.models import (
    CrowdAnalysis,
    ZoneDensity,
    ZoneType,
)


@pytest.fixture()
def mock_gemini_client():
    with patch("google.genai.Client") as mock_client:
        client_instance = mock_client.return_value
        yield client_instance


@pytest.mark.anyio()
async def test_get_fan_response_gemini_success(mock_gemini_client):
    # Setup mock response
    mock_model = mock_gemini_client.models
    mock_response = MagicMock()
    mock_response.text = '{"reply": "This is a Gemini reply", "language": "en", "suggested_actions": ["Action 1"]}'
    mock_model.generate_content.return_value = mock_response

    response = await get_fan_response(
        message="Where is food?",
        language="en",
        device_id="dev-123",
        use_gemini=True,
        project="test-proj",
        region="us-central1",
    )

    assert response.reply == "This is a Gemini reply"
    assert response.language == "en"
    assert response.source == "gemini"
    assert response.suggested_actions == ["Action 1"]


@pytest.mark.anyio()
async def test_get_fan_response_gemini_fallback_on_exception(mock_gemini_client):
    # Setup mock to raise exception
    mock_gemini_client.models.generate_content.side_effect = Exception("API error")

    response = await get_fan_response(
        message="Where can I eat?",
        language="en",
        device_id="dev-123",
        use_gemini=True,
        project="test-proj",
        region="us-central1",
    )

    # Should gracefully degrade to rules engine
    assert response.source == "rules"
    assert "food" in response.reply.lower() or "Food" in response.reply


@pytest.mark.anyio()
async def test_get_ops_recommendations_gemini_success(mock_gemini_client):
    mock_model = mock_gemini_client.models
    mock_response = MagicMock()
    mock_response.text = '{"recommendations": [{"action_type": "deploy_staff", "target_zone": "gate-a", "severity": "high", "reason": "Gate A is congested", "estimated_impact": "Reduce density"}]}'
    mock_model.generate_content.return_value = mock_response

    analysis = CrowdAnalysis(
        densities=[
            ZoneDensity(
                zone_id="gate-a",
                zone_type=ZoneType.GATE,
                current_count=2200,
                capacity=2500,
                density_pct=88.0,
                status="high",
            )
        ],
        hotspots=["gate-a"],
        total_occupancy=2200,
        total_capacity=2500,
        overall_density_pct=88.0,
        timestamp="2026-07-08T12:00:00Z",
    )

    recs = await get_ops_recommendations(
        analysis=analysis,
        use_gemini=True,
        project="test-proj",
        region="us-central1",
    )

    assert len(recs) == 1
    assert recs[0].action_type.value == "deploy_staff"
    assert recs[0].target_zone == "gate-a"
    assert recs[0].source == "gemini"


@pytest.mark.anyio()
async def test_get_ops_recommendations_gemini_fallback_on_exception(mock_gemini_client):
    mock_gemini_client.models.generate_content.side_effect = Exception("Quota exceeded")

    analysis = CrowdAnalysis(
        densities=[
            ZoneDensity(
                zone_id="gate-a",
                zone_type=ZoneType.GATE,
                current_count=2450,
                capacity=2500,
                density_pct=98.0,
                status="critical",
            )
        ],
        hotspots=["gate-a"],
        total_occupancy=2450,
        total_capacity=2500,
        overall_density_pct=98.0,
        timestamp="2026-07-08T12:00:00Z",
    )

    recs = await get_ops_recommendations(
        analysis=analysis,
        use_gemini=True,
        project="test-proj",
        region="us-central1",
    )

    assert len(recs) >= 1
    assert recs[0].source == "rules"
    assert recs[0].action_type.value == "redirect_crowd"
