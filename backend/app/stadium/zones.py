"""Stadium zone definitions for MetLife Stadium — FIFA World Cup 2026.

Pure data module: zone layout, adjacency graph, and accessibility metadata.
No I/O, no side effects. Zone data is based on MetLife Stadium's publicly
available layout and adapted for FIFA World Cup configuration.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.models import ZoneType


@dataclass(frozen=True)
class StadiumZone:
    """Immutable definition of a single stadium zone."""

    zone_id: str
    name: str
    zone_type: ZoneType
    capacity: int
    floor_level: int  # 0 = ground, 1 = lower bowl, 2 = upper bowl, 3 = suites
    is_accessible: bool = True
    has_elevator_access: bool = False
    adjacent_zones: tuple[str, ...] = field(default_factory=tuple)


# ---------------------------------------------------------------------------
# Zone definitions — MetLife Stadium FIFA WC 2026 configuration
# ---------------------------------------------------------------------------

VENUE_ZONES: dict[str, StadiumZone] = {
    # Gates — 4 cardinal entry points
    "gate-a": StadiumZone(
        zone_id="gate-a", name="Gate A (East)", zone_type=ZoneType.GATE,
        capacity=2500, floor_level=0, has_elevator_access=True,
        adjacent_zones=("concourse-lower-east", "parking-east"),
    ),
    "gate-b": StadiumZone(
        zone_id="gate-b", name="Gate B (West)", zone_type=ZoneType.GATE,
        capacity=2500, floor_level=0, has_elevator_access=True,
        adjacent_zones=("concourse-lower-west", "parking-west"),
    ),
    "gate-c": StadiumZone(
        zone_id="gate-c", name="Gate C (North)", zone_type=ZoneType.GATE,
        capacity=2000, floor_level=0, has_elevator_access=True,
        adjacent_zones=("concourse-lower-north", "transit-hub"),
    ),
    "gate-d": StadiumZone(
        zone_id="gate-d", name="Gate D (South)", zone_type=ZoneType.GATE,
        capacity=2000, floor_level=0, has_elevator_access=True,
        adjacent_zones=("concourse-lower-south", "parking-south"),
    ),
    # Lower concourses
    "concourse-lower-east": StadiumZone(
        zone_id="concourse-lower-east", name="Lower Concourse East",
        zone_type=ZoneType.CONCOURSE, capacity=5000, floor_level=1,
        has_elevator_access=True,
        adjacent_zones=("gate-a", "seating-lower-east", "concession-lower-east",
                        "restroom-lower-east", "concourse-lower-north",
                        "concourse-lower-south"),
    ),
    "concourse-lower-west": StadiumZone(
        zone_id="concourse-lower-west", name="Lower Concourse West",
        zone_type=ZoneType.CONCOURSE, capacity=5000, floor_level=1,
        has_elevator_access=True,
        adjacent_zones=("gate-b", "seating-lower-west", "concession-lower-west",
                        "restroom-lower-west", "concourse-lower-north",
                        "concourse-lower-south"),
    ),
    "concourse-lower-north": StadiumZone(
        zone_id="concourse-lower-north", name="Lower Concourse North",
        zone_type=ZoneType.CONCOURSE, capacity=4000, floor_level=1,
        has_elevator_access=True,
        adjacent_zones=("gate-c", "seating-lower-north", "concession-lower-north",
                        "concourse-lower-east", "concourse-lower-west"),
    ),
    "concourse-lower-south": StadiumZone(
        zone_id="concourse-lower-south", name="Lower Concourse South",
        zone_type=ZoneType.CONCOURSE, capacity=4000, floor_level=1,
        has_elevator_access=True,
        adjacent_zones=("gate-d", "seating-lower-south", "concession-lower-south",
                        "concourse-lower-east", "concourse-lower-west"),
    ),
    # Upper concourse
    "concourse-upper": StadiumZone(
        zone_id="concourse-upper", name="Upper Concourse",
        zone_type=ZoneType.CONCOURSE, capacity=8000, floor_level=2,
        has_elevator_access=True,
        adjacent_zones=("seating-upper-east", "seating-upper-west",
                        "concession-upper", "restroom-upper"),
    ),
    # Seating sections — lower bowl
    "seating-lower-east": StadiumZone(
        zone_id="seating-lower-east", name="Lower Bowl East",
        zone_type=ZoneType.SEATING, capacity=12000, floor_level=1,
        adjacent_zones=("concourse-lower-east",),
    ),
    "seating-lower-west": StadiumZone(
        zone_id="seating-lower-west", name="Lower Bowl West",
        zone_type=ZoneType.SEATING, capacity=12000, floor_level=1,
        adjacent_zones=("concourse-lower-west",),
    ),
    "seating-lower-north": StadiumZone(
        zone_id="seating-lower-north", name="Lower Bowl North (Behind Goal)",
        zone_type=ZoneType.SEATING, capacity=8000, floor_level=1,
        adjacent_zones=("concourse-lower-north",),
    ),
    "seating-lower-south": StadiumZone(
        zone_id="seating-lower-south", name="Lower Bowl South (Behind Goal)",
        zone_type=ZoneType.SEATING, capacity=8000, floor_level=1,
        adjacent_zones=("concourse-lower-south",),
    ),
    # Seating — upper bowl
    "seating-upper-east": StadiumZone(
        zone_id="seating-upper-east", name="Upper Bowl East",
        zone_type=ZoneType.SEATING, capacity=10000, floor_level=2,
        adjacent_zones=("concourse-upper",),
    ),
    "seating-upper-west": StadiumZone(
        zone_id="seating-upper-west", name="Upper Bowl West",
        zone_type=ZoneType.SEATING, capacity=10000, floor_level=2,
        adjacent_zones=("concourse-upper",),
    ),
    # Concessions
    "concession-lower-east": StadiumZone(
        zone_id="concession-lower-east", name="Food Court East",
        zone_type=ZoneType.CONCESSION, capacity=800, floor_level=1,
        adjacent_zones=("concourse-lower-east",),
    ),
    "concession-lower-west": StadiumZone(
        zone_id="concession-lower-west", name="Food Court West",
        zone_type=ZoneType.CONCESSION, capacity=800, floor_level=1,
        adjacent_zones=("concourse-lower-west",),
    ),
    "concession-lower-north": StadiumZone(
        zone_id="concession-lower-north", name="Food Court North",
        zone_type=ZoneType.CONCESSION, capacity=600, floor_level=1,
        adjacent_zones=("concourse-lower-north",),
    ),
    "concession-lower-south": StadiumZone(
        zone_id="concession-lower-south", name="Food Court South",
        zone_type=ZoneType.CONCESSION, capacity=600, floor_level=1,
        adjacent_zones=("concourse-lower-south",),
    ),
    "concession-upper": StadiumZone(
        zone_id="concession-upper", name="Upper Level Food Court",
        zone_type=ZoneType.CONCESSION, capacity=1000, floor_level=2,
        adjacent_zones=("concourse-upper",),
    ),
    # Restrooms
    "restroom-lower-east": StadiumZone(
        zone_id="restroom-lower-east", name="Restrooms Lower East",
        zone_type=ZoneType.RESTROOM, capacity=200, floor_level=1,
        adjacent_zones=("concourse-lower-east",),
    ),
    "restroom-lower-west": StadiumZone(
        zone_id="restroom-lower-west", name="Restrooms Lower West",
        zone_type=ZoneType.RESTROOM, capacity=200, floor_level=1,
        adjacent_zones=("concourse-lower-west",),
    ),
    "restroom-upper": StadiumZone(
        zone_id="restroom-upper", name="Restrooms Upper Level",
        zone_type=ZoneType.RESTROOM, capacity=300, floor_level=2,
        adjacent_zones=("concourse-upper",),
    ),
    # Special zones
    "medical-main": StadiumZone(
        zone_id="medical-main", name="Medical Station (Main)",
        zone_type=ZoneType.MEDICAL, capacity=50, floor_level=1,
        has_elevator_access=True,
        adjacent_zones=("concourse-lower-east",),
    ),
    "medical-field": StadiumZone(
        zone_id="medical-field", name="Field-Level Medical",
        zone_type=ZoneType.MEDICAL, capacity=30, floor_level=0,
        has_elevator_access=True,
        adjacent_zones=("gate-a",),
    ),
    "accessibility-center": StadiumZone(
        zone_id="accessibility-center", name="Accessibility Services Center",
        zone_type=ZoneType.ACCESSIBILITY, capacity=100, floor_level=1,
        has_elevator_access=True,
        adjacent_zones=("concourse-lower-east", "gate-a"),
    ),
    "sensory-room-1": StadiumZone(
        zone_id="sensory-room-1", name="Sensory Room 1",
        zone_type=ZoneType.ACCESSIBILITY, capacity=20, floor_level=1,
        has_elevator_access=True,
        adjacent_zones=("concourse-lower-east",),
    ),
    "sensory-room-2": StadiumZone(
        zone_id="sensory-room-2", name="Sensory Room 2",
        zone_type=ZoneType.ACCESSIBILITY, capacity=20, floor_level=1,
        has_elevator_access=True,
        adjacent_zones=("concourse-lower-west",),
    ),
    "vip-lounge": StadiumZone(
        zone_id="vip-lounge", name="VIP Hospitality Lounge",
        zone_type=ZoneType.VIP, capacity=2000, floor_level=3,
        has_elevator_access=True,
        adjacent_zones=("concourse-upper",),
    ),
    "media-center": StadiumZone(
        zone_id="media-center", name="Media Center",
        zone_type=ZoneType.MEDIA, capacity=500, floor_level=3,
        has_elevator_access=True,
        adjacent_zones=("concourse-upper",),
    ),
    "security-ops": StadiumZone(
        zone_id="security-ops", name="Security Operations Center",
        zone_type=ZoneType.SECURITY, capacity=50, floor_level=1,
        has_elevator_access=True,
        adjacent_zones=("concourse-lower-east",),
    ),
    # External zones
    "parking-east": StadiumZone(
        zone_id="parking-east", name="Parking Lot East",
        zone_type=ZoneType.PARKING, capacity=5000, floor_level=0,
        adjacent_zones=("gate-a",),
    ),
    "parking-west": StadiumZone(
        zone_id="parking-west", name="Parking Lot West",
        zone_type=ZoneType.PARKING, capacity=5000, floor_level=0,
        adjacent_zones=("gate-b",),
    ),
    "parking-south": StadiumZone(
        zone_id="parking-south", name="Parking Lot South",
        zone_type=ZoneType.PARKING, capacity=3000, floor_level=0,
        adjacent_zones=("gate-d",),
    ),
    "transit-hub": StadiumZone(
        zone_id="transit-hub", name="NJ Transit / Meadowlands Rail",
        zone_type=ZoneType.TRANSIT, capacity=4000, floor_level=0,
        adjacent_zones=("gate-c",),
    ),
}


def get_zone(zone_id: str) -> StadiumZone | None:
    """Look up a zone by ID. Returns None if not found."""
    return VENUE_ZONES.get(zone_id)


def get_zones_by_type(zone_type: ZoneType) -> list[StadiumZone]:
    """Return all zones of a given type."""
    return [z for z in VENUE_ZONES.values() if z.zone_type == zone_type]


def get_adjacent_zones(zone_id: str) -> list[StadiumZone]:
    """Return zones adjacent to the given zone."""
    zone = VENUE_ZONES.get(zone_id)
    if zone is None:
        return []
    return [VENUE_ZONES[adj] for adj in zone.adjacent_zones if adj in VENUE_ZONES]


def get_accessible_route(from_zone: str, to_zone: str) -> list[str] | None:
    """Find a path between zones using only accessible (elevator) routes.

    Uses BFS on the zone adjacency graph, filtering to zones with
    elevator access. Returns the zone ID path or None if no route.
    """
    if from_zone not in VENUE_ZONES or to_zone not in VENUE_ZONES:
        return None
    if from_zone == to_zone:
        return [from_zone]

    visited: set[str] = set()
    queue: list[list[str]] = [[from_zone]]

    while queue:
        path = queue.pop(0)
        current = path[-1]
        if current == to_zone:
            return path
        if current in visited:
            continue
        visited.add(current)
        zone = VENUE_ZONES[current]
        for neighbor_id in zone.adjacent_zones:
            if neighbor_id in visited or neighbor_id not in VENUE_ZONES:
                continue
            neighbor = VENUE_ZONES[neighbor_id]
            # Accessible route: only traverse zones with elevator access
            if neighbor.has_elevator_access or neighbor.zone_id == to_zone:
                queue.append([*path, neighbor_id])

    return None
