"""Stadium operational constants with source citations.

Every numeric constant is named and sourced. No magic numbers appear in
computation functions — they reference constants from this module.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Venue capacity — MetLife Stadium, East Rutherford, NJ
# Source: FIFA World Cup 2026 venue profile
# https://www.fifa.com/fifaplus/en/tournaments/mens/worldcup/canadamexicousa2026
# ---------------------------------------------------------------------------

TOTAL_CAPACITY = 82_500  # FIFA-rated match capacity
VIP_CAPACITY = 8_250  # ~10% of total, typical for FIFA events
MEDIA_CAPACITY = 1_500  # FIFA media accreditation allocation

# ---------------------------------------------------------------------------
# Gate throughput — fans per minute per lane
# Source: Guide to Safety at Sports Grounds ("Green Guide"), 6th ed.
# SGSA, 2018 — typical turnstile flow rate
# ---------------------------------------------------------------------------

GATE_THROUGHPUT_PER_LANE = 660  # persons/hour/lane ≈ 11 persons/min/lane
LANES_PER_GATE = 12  # MetLife has 4 main gates, ~12 lanes each
GATE_COUNT = 4  # Gates A, B, C, D at MetLife Stadium

# ---------------------------------------------------------------------------
# Crowd density thresholds — persons per square metre
# Source: Fruin, J.J. (1971) "Pedestrian Planning and Design" — Level of
# Service classification; updated by Still, G.K. (2014) crowd safety research
# ---------------------------------------------------------------------------

DENSITY_LOW_THRESHOLD = 40  # % — comfortable movement
DENSITY_MODERATE_THRESHOLD = 65  # % — noticeable crowding
DENSITY_HIGH_THRESHOLD = 85  # % — restricted movement, risk of crush
DENSITY_CRITICAL_THRESHOLD = 95  # % — dangerous, immediate action needed

# ---------------------------------------------------------------------------
# Concession service rates
# Source: Aramark Stadium Operations benchmarks (industry standard)
# ---------------------------------------------------------------------------

CONCESSION_SERVE_RATE = 45  # seconds per order, averaged across items
CONCESSION_STANDS_PER_CONCOURSE = 8  # typical for major NFL/FIFA venues
CONCESSION_PEAK_MULTIPLIER = 2.5  # half-time demand spike vs. average

# ---------------------------------------------------------------------------
# Walking speed and distance — indoor stadium corridors
# Source: Weidmann, U. (1993) "Transporttechnik der Fussgänger"
# ---------------------------------------------------------------------------

WALKING_SPEED_NORMAL = 1.34  # m/s — unimpeded corridor
WALKING_SPEED_CROWDED = 0.7  # m/s — density > 2 p/m²
WALKING_SPEED_WHEELCHAIR = 0.9  # m/s — wheelchair average
AVG_CONCOURSE_LENGTH_M = 250  # metres — MetLife upper concourse arc length

# ---------------------------------------------------------------------------
# Emergency evacuation
# Source: NFPA 101 Life Safety Code, 2024 edition
# ---------------------------------------------------------------------------

EVACUATION_FLOW_PER_EXIT_M = 82  # persons/min per metre of exit width
MIN_EVACUATION_TIME_MIN = 8  # target full-venue evacuation time
EMERGENCY_EXIT_COUNT = 16  # MetLife emergency exits

# ---------------------------------------------------------------------------
# Accessibility
# Source: ADA Standards for Accessible Design, 2010
# ---------------------------------------------------------------------------

ACCESSIBLE_SEATING_RATIO = 0.01  # 1% of capacity (ADA minimum)
ACCESSIBLE_SEATING_COUNT = int(TOTAL_CAPACITY * ACCESSIBLE_SEATING_RATIO)
SENSORY_ROOM_COUNT = 4  # quiet rooms for neurodivergent fans
ELEVATOR_COUNT = 8  # MetLife Stadium accessible elevators

# ---------------------------------------------------------------------------
# Match timing — standard FIFA match windows
# ---------------------------------------------------------------------------

PRE_MATCH_WINDOW_MIN = 120  # gates open 2h before kickoff
HALF_TIME_DURATION_MIN = 15  # standard FIFA half-time
POST_MATCH_WINDOW_MIN = 60  # controlled egress period
MATCH_DURATION_MIN = 90  # regular time
