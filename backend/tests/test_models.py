"""Tests for Pydantic models — bounded field validation."""

import pytest
from pydantic import ValidationError

from app.models import ChatRequest, CrowdSnapshot, OpsActionRequest, ZoneOccupancy, ZoneType


def test_chat_request_rejects_oversized_message():
    with pytest.raises(ValidationError):
        ChatRequest(message="x" * 2001, language="en", device_id="abc123")


def test_chat_request_rejects_invalid_language_code():
    with pytest.raises(ValidationError):
        ChatRequest(message="hello", language="invalid!", device_id="abc123")


def test_chat_request_accepts_valid_input():
    req = ChatRequest(message="Where is Gate A?", language="en", device_id="dev-001")
    assert req.message == "Where is Gate A?"
    assert req.language == "en"


def test_zone_occupancy_rejects_negative_count():
    with pytest.raises(ValidationError):
        ZoneOccupancy(zone_id="z1", current_count=-1, capacity=100, zone_type=ZoneType.GATE)


def test_zone_occupancy_rejects_over_capacity():
    with pytest.raises(ValidationError):
        ZoneOccupancy(
            zone_id="z1", current_count=200000,
            capacity=100, zone_type=ZoneType.GATE,
        )


def test_ops_action_rejects_invalid_action_type():
    with pytest.raises(ValidationError):
        OpsActionRequest(
            action_type="invalid_action",
            target_zone="gate-a",
            operator_id="staff-001",
        )


def test_ops_action_accepts_valid_input():
    action = OpsActionRequest(
        action_type="deploy_staff",
        target_zone="gate-a",
        operator_id="staff-001",
        notes="Deploying stewards",
    )
    assert action.action_type.value == "deploy_staff"


def test_crowd_snapshot_rejects_too_many_zones():
    zones = [
        ZoneOccupancy(zone_id=f"z{i}", current_count=10, capacity=100, zone_type=ZoneType.SEATING)
        for i in range(51)  # MAX_ZONES = 50
    ]
    with pytest.raises(ValidationError):
        CrowdSnapshot(zones=zones)
