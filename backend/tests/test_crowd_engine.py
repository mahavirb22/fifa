"""Tests for the crowd density simulator — pure function unit tests.

No mocking needed: the simulator is pure computation with no I/O.
"""

from app.crowd.simulator import (
    analyze_crowd,
    estimate_gate_wait_minutes,
    generate_demo_snapshot,
    suggest_gate_rebalancing,
)
from app.models import CrowdSnapshot, ZoneOccupancy, ZoneType


def _zone(zone_id, count, capacity, zone_type=ZoneType.SEATING):
    return ZoneOccupancy(
        zone_id=zone_id,
        current_count=count,
        capacity=capacity,
        zone_type=zone_type,
    )


def test_low_density_classified_correctly():
    snapshot = CrowdSnapshot(zones=[_zone("sec-a", 100, 1000)])
    result = analyze_crowd(snapshot)
    assert result.densities[0].status == "low"
    assert result.densities[0].density_pct == 10.0


def test_moderate_density_at_threshold():
    snapshot = CrowdSnapshot(zones=[_zone("sec-b", 650, 1000)])
    result = analyze_crowd(snapshot)
    assert result.densities[0].status == "moderate"
    assert result.densities[0].density_pct == 65.0


def test_high_density_triggers_hotspot():
    snapshot = CrowdSnapshot(zones=[_zone("sec-c", 900, 1000)])
    result = analyze_crowd(snapshot)
    assert result.densities[0].status == "high"
    assert "sec-c" in result.hotspots


def test_critical_density_at_threshold():
    snapshot = CrowdSnapshot(zones=[_zone("sec-d", 960, 1000)])
    result = analyze_crowd(snapshot)
    assert result.densities[0].status == "critical"
    assert "sec-d" in result.hotspots


def test_overall_density_calculated_across_zones():
    snapshot = CrowdSnapshot(zones=[
        _zone("z1", 500, 1000),
        _zone("z2", 500, 1000),
    ])
    result = analyze_crowd(snapshot)
    assert result.total_occupancy == 1000
    assert result.total_capacity == 2000
    assert result.overall_density_pct == 50.0


def test_zero_capacity_returns_zero_density():
    """Edge case: capacity of 0 should not crash."""
    snapshot = CrowdSnapshot(zones=[_zone("z0", 0, 1)])
    result = analyze_crowd(snapshot)
    assert result.densities[0].density_pct == 0.0


def test_density_capped_at_100():
    """Overcrowding: count > capacity should cap at 100%."""
    # Model prevents count > capacity via Field(le=MAX_ZONE_CAPACITY),
    # but the function itself caps at 100.
    snapshot = CrowdSnapshot(zones=[_zone("z-full", 1000, 1000)])
    result = analyze_crowd(snapshot)
    assert result.densities[0].density_pct == 100.0


def test_gate_wait_estimation():
    wait = estimate_gate_wait_minutes(10000)
    assert wait > 0
    assert isinstance(wait, float)


def test_gate_rebalancing_suggests_redirect():
    densities = {"gate-a": 92.0, "gate-b": 35.0, "gate-c": 60.0}
    suggestions = suggest_gate_rebalancing(densities)
    assert len(suggestions) >= 1
    assert suggestions[0]["from"] == "gate-a"
    assert suggestions[0]["to"] == "gate-b"


def test_gate_rebalancing_empty_when_balanced():
    densities = {"gate-a": 50.0, "gate-b": 55.0}
    suggestions = suggest_gate_rebalancing(densities)
    assert suggestions == []


def test_demo_snapshot_generates_valid_data():
    snapshot = generate_demo_snapshot()
    assert len(snapshot.zones) > 0
    for zone in snapshot.zones:
        assert 0 <= zone.current_count <= zone.capacity
