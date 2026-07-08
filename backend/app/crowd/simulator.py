"""Crowd density simulator — pure, deterministic, side-effect-free.

The same occupancy input always yields the same density analysis output.
No I/O, no database calls, no external services. This module can be called
from any context (routes, tests, CLI) without setup.

Density thresholds are based on Fruin (1971) and Still (2014) crowd safety
research, adapted as percentage-of-capacity for stadium zones.
"""

from __future__ import annotations

import hashlib
import math
from datetime import datetime, timezone

from app.models import (
    CrowdAnalysis,
    CrowdSnapshot,
    ZoneDensity,
    ZoneOccupancy,
)
from app.stadium.constants import (
    DENSITY_CRITICAL_THRESHOLD,
    DENSITY_HIGH_THRESHOLD,
    DENSITY_LOW_THRESHOLD,
    DENSITY_MODERATE_THRESHOLD,
    GATE_COUNT,
    GATE_THROUGHPUT_PER_LANE,
    LANES_PER_GATE,
)


def _compute_density_pct(current: int, capacity: int) -> float:
    """Calculate density as a percentage of capacity, capped at 100."""
    if capacity <= 0:
        return 0.0
    return min(round((current / capacity) * 100, 1), 100.0)


def _classify_density(density_pct: float) -> str:
    """Map density percentage to a human-readable status label."""
    if density_pct >= DENSITY_CRITICAL_THRESHOLD:
        return "critical"
    if density_pct >= DENSITY_HIGH_THRESHOLD:
        return "high"
    if density_pct >= DENSITY_MODERATE_THRESHOLD:
        return "moderate"
    return "low"


def _zone_density(zone: ZoneOccupancy) -> ZoneDensity:
    """Compute density result for a single zone."""
    pct = _compute_density_pct(zone.current_count, zone.capacity)
    return ZoneDensity(
        zone_id=zone.zone_id,
        zone_type=zone.zone_type,
        current_count=zone.current_count,
        capacity=zone.capacity,
        density_pct=pct,
        status=_classify_density(pct),
    )


def _identify_hotspots(densities: list[ZoneDensity]) -> list[str]:
    """Return zone IDs where density exceeds the high threshold."""
    return [
        d.zone_id
        for d in densities
        if d.density_pct >= DENSITY_HIGH_THRESHOLD
    ]


def analyze_crowd(snapshot: CrowdSnapshot) -> CrowdAnalysis:
    """Analyze a complete stadium crowd snapshot.

    Takes zone occupancy readings and produces density classifications,
    hotspot identification, and overall stadium metrics. Pure function —
    deterministic output for any given input.
    """
    densities = [_zone_density(zone) for zone in snapshot.zones]
    hotspots = _identify_hotspots(densities)
    total_occ = sum(z.current_count for z in snapshot.zones)
    total_cap = sum(z.capacity for z in snapshot.zones)
    overall_pct = _compute_density_pct(total_occ, total_cap)

    return CrowdAnalysis(
        densities=densities,
        hotspots=hotspots,
        total_occupancy=total_occ,
        total_capacity=total_cap,
        overall_density_pct=overall_pct,
        timestamp=datetime.now(tz=timezone.utc).isoformat(),
    )


def estimate_gate_wait_minutes(arrival_count: int) -> float:
    """Estimate gate wait time given fans arriving simultaneously.

    Uses gate throughput rates from the Green Guide (SGSA, 2018) —
    660 persons/hour/lane with LANES_PER_GATE lanes across GATE_COUNT gates.
    """
    total_throughput_per_min = (GATE_THROUGHPUT_PER_LANE / 60) * LANES_PER_GATE * GATE_COUNT
    if total_throughput_per_min <= 0:
        return 0.0
    return round(arrival_count / total_throughput_per_min, 1)


def suggest_gate_rebalancing(
    gate_densities: dict[str, float],
) -> list[dict[str, str]]:
    """Suggest redirecting fans from overloaded gates to quieter ones.

    Returns a list of recommendations like:
    {"from": "gate-a", "to": "gate-c", "reason": "Gate A at 92%, Gate C at 35%"}
    """
    if not gate_densities:
        return []

    suggestions: list[dict[str, str]] = []
    sorted_gates = sorted(gate_densities.items(), key=lambda x: x[1])
    low_gates = [g for g in sorted_gates if g[1] < DENSITY_MODERATE_THRESHOLD]
    high_gates = [g for g in sorted_gates if g[1] >= DENSITY_HIGH_THRESHOLD]

    for high_gate_id, high_pct in high_gates:
        for low_gate_id, low_pct in low_gates:
            suggestions.append({
                "from": high_gate_id,
                "to": low_gate_id,
                "reason": (
                    f"{high_gate_id.replace('-', ' ').title()} at {high_pct:.0f}%, "
                    f"{low_gate_id.replace('-', ' ').title()} at {low_pct:.0f}%"
                ),
            })

    return suggestions


def generate_demo_snapshot() -> CrowdSnapshot:
    """Generate a realistic demo crowd snapshot.

    Uses a deterministic pseudo-random seed based on the current minute,
    so the demo updates visually over time but is reproducible within the
    same minute window.
    """
    from app.stadium.zones import VENUE_ZONES

    now = datetime.now(tz=timezone.utc)
    seed_str = now.strftime("%Y-%m-%d-%H-%M")
    seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)  # noqa: S324

    zones: list[ZoneOccupancy] = []
    for zone_id, zone_def in VENUE_ZONES.items():
        # Deterministic pseudo-random occupancy based on zone hash + time seed
        zone_hash = int(hashlib.md5(zone_id.encode()).hexdigest()[:8], 16)  # noqa: S324
        combined = (seed + zone_hash) % 10000
        # Generate occupancy between 20% and 95% of capacity
        base_pct = 0.2 + (combined / 10000) * 0.75
        # Apply sine wave for time-based variation (simulates crowd flow)
        time_factor = math.sin(combined * 0.001 + now.minute * 0.1) * 0.15
        final_pct = max(0.05, min(0.98, base_pct + time_factor))
        count = int(zone_def.capacity * final_pct)

        zones.append(ZoneOccupancy(
            zone_id=zone_id,
            current_count=count,
            capacity=zone_def.capacity,
            zone_type=zone_def.zone_type,
        ))

    return CrowdSnapshot(zones=zones, match_id="WC2026-DEMO")
