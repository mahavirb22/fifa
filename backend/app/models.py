"""Pydantic models serving as validated API contracts.

Every field has explicit bounds (ge, le, min_length, max_length, pattern) to
prevent invalid or malicious inputs from reaching business logic. Models double
as OpenAPI documentation — the schema IS the validation.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Named upper-bound constants — each with a rationale
# ---------------------------------------------------------------------------

MAX_MESSAGE_LENGTH = 2000  # Generous for multilingual queries; prevents abuse
MAX_DEVICE_ID_LENGTH = 128  # UUID is 36 chars; allow padding for custom IDs
MAX_ZONE_CAPACITY = 100_000  # MetLife Stadium total capacity is ~82,500
MAX_DENSITY_PERCENT = 100  # Percentage cannot exceed 100
MAX_ZONES = 50  # Realistic stadium zone count
MAX_LANGUAGE_CODE_LENGTH = 10  # e.g. "pt-BR", "zh-Hans"
MAX_RECOMMENDATIONS = 20  # Cap AI recommendation count
MAX_SUMMARY_LENGTH = 5000  # AI response text limit


# ---------------------------------------------------------------------------
# Enums — finite sets that make invalid states unrepresentable
# ---------------------------------------------------------------------------


class ZoneType(str, Enum):
    """Stadium zone categories — based on FIFA venue specifications."""

    GATE = "gate"
    CONCOURSE = "concourse"
    SEATING = "seating"
    CONCESSION = "concession"
    RESTROOM = "restroom"
    MEDICAL = "medical"
    ACCESSIBILITY = "accessibility"
    VIP = "vip"
    MEDIA = "media"
    SECURITY = "security"
    PARKING = "parking"
    TRANSIT = "transit"


class AlertSeverity(str, Enum):
    """Operational alert severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ActionType(str, Enum):
    """Types of operational actions staff can take."""

    OPEN_GATE = "open_gate"
    CLOSE_GATE = "close_gate"
    REDIRECT_CROWD = "redirect_crowd"
    DEPLOY_STAFF = "deploy_staff"
    ALERT_SECURITY = "alert_security"
    CALL_MEDICAL = "call_medical"
    ADJUST_CONCESSIONS = "adjust_concessions"
    MAKE_ANNOUNCEMENT = "make_announcement"


# ---------------------------------------------------------------------------
# Chat models — Fan Assistant
# ---------------------------------------------------------------------------


class ChatRequest(BaseModel):
    """Fan assistant chat input — validated before any AI processing."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=MAX_MESSAGE_LENGTH,
        description="Fan's question or request in any language",
    )
    language: str = Field(
        default="en",
        min_length=2,
        max_length=MAX_LANGUAGE_CODE_LENGTH,
        pattern=r"^[a-z]{2}(-[A-Za-z]{2,4})?$",
        description="ISO 639-1 language code, optionally with region (e.g. pt-BR)",
    )
    device_id: str = Field(
        ...,
        min_length=1,
        max_length=MAX_DEVICE_ID_LENGTH,
        pattern=r"^[A-Za-z0-9_-]+$",
        description="Anonymous client-generated device identifier",
    )


class ChatResponse(BaseModel):
    """Fan assistant response — always returned, even on AI failure."""

    reply: str = Field(..., description="Response text in the requested language")
    language: str = Field(..., description="Language of the response")
    source: Literal["gemini", "rules", "cache"] = Field(
        ..., description="Which engine produced this response"
    )
    suggested_actions: list[str] = Field(
        default_factory=list,
        description="Suggested follow-up actions for the fan",
    )


# ---------------------------------------------------------------------------
# Crowd models — Density & Heatmap
# ---------------------------------------------------------------------------


class ZoneOccupancy(BaseModel):
    """Occupancy reading for a single stadium zone."""

    zone_id: str = Field(
        ...,
        min_length=1,
        max_length=64,
        pattern=r"^[A-Za-z0-9_-]+$",
        description="Unique zone identifier",
    )
    current_count: int = Field(
        ..., ge=0, le=MAX_ZONE_CAPACITY, description="Current headcount in zone"
    )
    capacity: int = Field(
        ..., ge=1, le=MAX_ZONE_CAPACITY, description="Maximum zone capacity"
    )
    zone_type: ZoneType = Field(..., description="Category of this zone")


class CrowdSnapshot(BaseModel):
    """Complete stadium occupancy snapshot at a point in time."""

    zones: list[ZoneOccupancy] = Field(
        ...,
        min_length=1,
        max_length=MAX_ZONES,
        description="Occupancy data for every active zone",
    )
    match_id: str = Field(
        default="WC2026-DEMO",
        min_length=1,
        max_length=64,
        description="Match identifier",
    )


class ZoneDensity(BaseModel):
    """Computed density result for a single zone."""

    zone_id: str
    zone_type: ZoneType
    current_count: int
    capacity: int
    density_pct: float = Field(..., ge=0, le=MAX_DENSITY_PERCENT)
    status: Literal["low", "moderate", "high", "critical"]


class CrowdAnalysis(BaseModel):
    """Full crowd analysis output from the simulator."""

    densities: list[ZoneDensity]
    hotspots: list[str] = Field(default_factory=list, description="Zone IDs above threshold")
    total_occupancy: int = Field(ge=0)
    total_capacity: int = Field(ge=1)
    overall_density_pct: float = Field(ge=0, le=MAX_DENSITY_PERCENT)
    timestamp: str


# ---------------------------------------------------------------------------
# Operations models — Recommendations & Actions
# ---------------------------------------------------------------------------


class OpsRecommendation(BaseModel):
    """AI-generated operational recommendation."""

    action_type: ActionType
    target_zone: str
    severity: AlertSeverity
    reason: str = Field(..., max_length=MAX_SUMMARY_LENGTH)
    estimated_impact: str = Field(default="", max_length=MAX_SUMMARY_LENGTH)
    source: Literal["gemini", "rules", "cache"] = Field(default="rules")


class OpsActionRequest(BaseModel):
    """Staff-submitted operational action."""

    action_type: ActionType
    target_zone: str = Field(..., min_length=1, max_length=64)
    notes: str = Field(default="", max_length=MAX_MESSAGE_LENGTH)
    operator_id: str = Field(
        ...,
        min_length=1,
        max_length=MAX_DEVICE_ID_LENGTH,
        pattern=r"^[A-Za-z0-9_-]+$",
    )


class OpsActionRecord(BaseModel):
    """Persisted record of an operational action."""

    id: str
    action_type: ActionType
    target_zone: str
    notes: str
    operator_id: str
    created_at: datetime
    source: Literal["gemini", "rules", "cache"] = "rules"


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


class HealthStatus(BaseModel):
    """Service health response."""

    status: Literal["healthy", "degraded"]
    version: str
    gemini_available: bool
    firestore_available: bool
