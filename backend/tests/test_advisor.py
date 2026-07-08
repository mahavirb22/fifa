"""Tests for the AI advisor — rules engine, validation, and degradation."""

import pytest

from app.advisor.gemini import _validate_fan_response, _validate_ops_response
from app.advisor.rules import generate_ops_recommendations, handle_fan_query
from app.models import (
    CrowdAnalysis,
    ZoneDensity,
    ZoneType,
)


# ---------------------------------------------------------------------------
# Fan query rules engine tests
# ---------------------------------------------------------------------------


def test_food_keyword_returns_food_response():
    result = handle_fan_query("Where can I get food?", "en")
    assert "food" in result["reply"].lower() or "Food" in result["reply"]


def test_restroom_keyword_returns_restroom_response():
    result = handle_fan_query("bathroom please", "en")
    assert "restroom" in result["reply"].lower() or "Restroom" in result["reply"]


def test_spanish_food_query_returns_spanish():
    result = handle_fan_query("dónde puedo comer", "es")
    assert result["language"] == "es"
    # Should contain Spanish text
    assert "comida" in result["reply"].lower() or "Patio" in result["reply"]


def test_unknown_language_falls_back_to_english():
    result = handle_fan_query("hello", "xx")
    assert result["language"] == "xx"
    # Falls back to English text
    assert "welcome" in result["reply"].lower() or "Welcome" in result["reply"]


def test_accessibility_query_returns_accessibility_info():
    result = handle_fan_query("wheelchair accessible seating", "en")
    assert "wheelchair" in result["reply"].lower() or "accessibility" in result["reply"].lower()


def test_medical_query_returns_medical_info():
    result = handle_fan_query("I need a doctor", "en")
    assert "medical" in result["reply"].lower() or "Medical" in result["reply"]


def test_default_response_includes_suggestions():
    result = handle_fan_query("hello there!", "en")
    assert isinstance(result.get("suggested_actions"), list)
    assert len(result["suggested_actions"]) > 0


# ---------------------------------------------------------------------------
# Operations recommendations tests
# ---------------------------------------------------------------------------


def _make_analysis(densities_data):
    densities = [
        ZoneDensity(
            zone_id=d[0], zone_type=d[1],
            current_count=d[2], capacity=d[3],
            density_pct=d[4], status=d[5],
        )
        for d in densities_data
    ]
    total_occ = sum(d.current_count for d in densities)
    total_cap = sum(d.capacity for d in densities)
    return CrowdAnalysis(
        densities=densities,
        hotspots=[d.zone_id for d in densities if d.density_pct >= 85],
        total_occupancy=total_occ,
        total_capacity=total_cap,
        overall_density_pct=round(total_occ / total_cap * 100, 1),
        timestamp="2026-07-07T12:00:00Z",
    )


def test_critical_zone_generates_redirect_recommendation():
    analysis = _make_analysis([
        ("gate-a", ZoneType.GATE, 2400, 2500, 96.0, "critical"),
    ])
    recs = generate_ops_recommendations(analysis)
    assert any(r.action_type.value == "redirect_crowd" for r in recs)
    assert any(r.severity.value == "critical" for r in recs)


def test_high_density_generates_staff_deployment():
    analysis = _make_analysis([
        ("concourse-lower-east", ZoneType.CONCOURSE, 4500, 5000, 90.0, "high"),
    ])
    recs = generate_ops_recommendations(analysis)
    assert any(r.action_type.value == "deploy_staff" for r in recs)


def test_concession_overcrowding_triggers_adjustment():
    analysis = _make_analysis([
        ("concession-lower-east", ZoneType.CONCESSION, 600, 800, 75.0, "moderate"),
    ])
    recs = generate_ops_recommendations(analysis)
    assert any(r.action_type.value == "adjust_concessions" for r in recs)


def test_gate_imbalance_triggers_announcement():
    analysis = _make_analysis([
        ("gate-a", ZoneType.GATE, 2250, 2500, 90.0, "high"),
        ("gate-b", ZoneType.GATE, 750, 2500, 30.0, "low"),
    ])
    recs = generate_ops_recommendations(analysis)
    assert any(r.action_type.value == "make_announcement" for r in recs)


def test_no_recommendations_for_low_density():
    analysis = _make_analysis([
        ("seating-lower-east", ZoneType.SEATING, 3000, 12000, 25.0, "low"),
    ])
    recs = generate_ops_recommendations(analysis)
    # Only crowd-based recs — low density should have none
    assert len(recs) == 0


# ---------------------------------------------------------------------------
# Validation tests
# ---------------------------------------------------------------------------


def test_validate_fan_response_rejects_missing_reply():
    with pytest.raises(ValueError, match="reply"):
        _validate_fan_response({"language": "en"})


def test_validate_fan_response_rejects_long_reply():
    with pytest.raises(ValueError, match="too long"):
        _validate_fan_response({"reply": "x" * 6000, "language": "en"})


def test_validate_fan_response_rejects_unknown_language():
    with pytest.raises(ValueError, match="Unknown language"):
        _validate_fan_response({"reply": "hello", "language": "zz-FAKE"})


def test_validate_fan_response_accepts_valid_response():
    _validate_fan_response({
        "reply": "Welcome!",
        "language": "en",
        "suggested_actions": ["Find food"],
    })
