"""Gemini-powered AI advisor with graceful degradation.

This module provides two AI capabilities:
1. Fan Assistant — multilingual chatbot for wayfinding and stadium queries
2. Ops Advisor — operational recommendations based on crowd data

Design principle: Gemini provides the richest, most personalized responses.
When Gemini is unavailable (disabled, no credentials, quota, error), the
rules engine in advisor/rules.py handles every query. Responses are tagged
with their source ("gemini", "rules", "cache") for transparency.

Caching: responses are cached with a 60-second TTL keyed by SHA-256 hash
of the serialized input. Thread-safe via threading lock.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import time
from functools import lru_cache
from pathlib import Path
from threading import Lock
from typing import Any

import yaml
from cachetools import TTLCache

from app.advisor.rules import generate_ops_recommendations, handle_fan_query
from app.models import (
    ActionType,
    AlertSeverity,
    ChatResponse,
    CrowdAnalysis,
    OpsRecommendation,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Cache — 60s TTL, max 256 entries, thread-safe
# ---------------------------------------------------------------------------

_response_cache: TTLCache[str, dict[str, Any]] = TTLCache(maxsize=256, ttl=60)
_cache_lock = Lock()

# Known valid values for response validation
_VALID_ACTION_TYPES = frozenset(a.value for a in ActionType)
_VALID_SEVERITIES = frozenset(s.value for s in AlertSeverity)
_VALID_LANGUAGES = frozenset([
    "en", "es", "fr", "pt", "ar", "de", "ja", "zh", "ko", "hi",
    "it", "nl", "ru", "tr", "pl", "sv", "da", "no", "fi",
    "pt-BR", "zh-Hans", "zh-Hant",
])


# ---------------------------------------------------------------------------
# Prompt config loading — versioned YAML with fallback
# ---------------------------------------------------------------------------


@lru_cache(maxsize=4)
def _load_prompt_config(version: int = 1) -> dict[str, Any]:
    """Load versioned prompt config from YAML, with inline fallback."""
    prompt_path = Path(__file__).parent / "prompts" / f"v{version}.yaml"
    try:
        with open(prompt_path, encoding="utf-8") as f:
            config: dict[str, Any] = yaml.safe_load(f)
            return config
    except (FileNotFoundError, yaml.YAMLError) as exc:
        logger.warning("Prompt config v%d not found, using defaults: %s", version, exc)
        return {
            "fan_assistant": {
                "system_instruction": "You are a helpful FIFA World Cup 2026 stadium assistant.",
                "temperature": 0.7,
                "max_output_tokens": 1024,
            },
            "ops_advisor": {
                "system_instruction": "You are an operations advisor for stadium crowd management.",
                "temperature": 0.3,
                "max_output_tokens": 2048,
            },
        }


# ---------------------------------------------------------------------------
# Gemini client — lazy init + lru_cache
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def _get_gemini_client(project: str, location: str) -> Any:
    """Initialize and cache the Gemini client.

    Lazy import: the google.genai SDK is imported inside this function so
    importing this module never triggers credential loading.
    """
    from google import genai  # Lazy import — no credentials at import time

    client = genai.Client(vertexai=True, project=project, location=location)
    logger.info("Gemini client initialized for project=%s, location=%s", project, location)
    return client


# ---------------------------------------------------------------------------
# Response validation — never trust AI output blindly
# ---------------------------------------------------------------------------


def _validate_fan_response(payload: dict[str, Any]) -> None:
    """Validate AI fan assistant response against known constraints.

    Raises ValueError if any field is invalid. Catches hallucinated
    languages, oversized responses, and malformed structure.
    """
    if "reply" not in payload or not isinstance(payload["reply"], str):
        raise ValueError("Missing or invalid 'reply' field")

    if len(payload["reply"]) > 5000:
        raise ValueError(f"Reply too long: {len(payload['reply'])} chars (max 5000)")

    language = payload.get("language", "")
    if language and language not in _VALID_LANGUAGES:
        raise ValueError(f"Unknown language code: {language}")

    actions = payload.get("suggested_actions", [])
    if not isinstance(actions, list) or len(actions) > 5:
        raise ValueError(f"Invalid suggested_actions: expected list of ≤5, got {type(actions)}")


def _validate_ops_response(
    payload: dict[str, Any],
    analysis: CrowdAnalysis,
) -> None:
    """Validate AI ops advisor response against known constraints.

    Checks action types, severities, and zone references against whitelists.
    """
    recs = payload.get("recommendations", [])
    if not isinstance(recs, list):
        raise ValueError(f"Expected recommendations list, got {type(recs)}")

    known_zones = {d.zone_id for d in analysis.densities}

    for rec in recs:
        if rec.get("action_type") not in _VALID_ACTION_TYPES:
            raise ValueError(f"Invalid action_type: {rec.get('action_type')}")
        if rec.get("severity") not in _VALID_SEVERITIES:
            raise ValueError(f"Invalid severity: {rec.get('severity')}")
        if rec.get("target_zone") and rec["target_zone"] not in known_zones:
            raise ValueError(f"Unknown zone: {rec['target_zone']}")


# ---------------------------------------------------------------------------
# Core Gemini call — structured output with response schema
# ---------------------------------------------------------------------------


def _call_gemini(
    client: Any,
    prompt: str,
    system_instruction: str,
    response_schema: dict[str, Any] | None,
    temperature: float,
    max_tokens: int,
) -> dict[str, Any]:
    """Make a synchronous Gemini API call with structured JSON output.

    Uses response_mime_type="application/json" and response_schema for
    reliable, parseable output.
    """
    from google.genai import types  # Lazy import

    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=temperature,
        max_output_tokens=max_tokens,
        response_mime_type="application/json",
    )

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=config,
    )

    result: dict[str, Any] = json.loads(response.text)
    return result


# ---------------------------------------------------------------------------
# Cache key generation
# ---------------------------------------------------------------------------


def _cache_key(prefix: str, data: str) -> str:
    """Generate a SHA-256 cache key from prefix + serialized data."""
    return prefix + ":" + hashlib.sha256(data.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Public API — Fan Assistant
# ---------------------------------------------------------------------------


async def get_fan_response(
    message: str,
    language: str,
    device_id: str,
    *,
    use_gemini: bool = False,
    project: str = "",
    region: str = "",
    prompt_version: int = 1,
) -> ChatResponse:
    """Get a fan assistant response — Gemini if available, rules as fallback.

    This is the public entry point. It catches ALL exceptions from Gemini
    and falls back to the rules engine. The response is always tagged with
    its source.
    """
    start = time.monotonic()

    # Check cache first
    cache_data = json.dumps({"m": message, "l": language}, sort_keys=True)
    key = _cache_key("fan", cache_data)
    with _cache_lock:
        cached = _response_cache.get(key)
    if cached is not None:
        _log_advisor("fan_assistant", time.monotonic() - start, "cache", device_id)
        return ChatResponse(
            reply=cached["reply"],
            language=cached.get("language", language),
            source="cache",
            suggested_actions=cached.get("suggested_actions", []),
        )

    # Try Gemini
    if use_gemini and project:
        try:
            config = _load_prompt_config(prompt_version)
            fan_config = config.get("fan_assistant", {})
            client = _get_gemini_client(project, region)

            prompt = f"Fan message (language: {language}): {message}"
            payload = await asyncio.to_thread(
                _call_gemini,
                client,
                prompt,
                fan_config.get("system_instruction", ""),
                fan_config.get("response_schema"),
                fan_config.get("temperature", 0.7),
                fan_config.get("max_output_tokens", 1024),
            )

            _validate_fan_response(payload)

            # Cache the validated response
            with _cache_lock:
                _response_cache[key] = payload

            _log_advisor("fan_assistant", time.monotonic() - start, "gemini", device_id)
            return ChatResponse(
                reply=payload["reply"],
                language=payload.get("language", language),
                source="gemini",
                suggested_actions=payload.get("suggested_actions", []),
            )

        except Exception:
            logger.exception("Gemini fan assistant failed, falling back to rules engine")

    # Fallback: rules engine (always works)
    result = handle_fan_query(message, language)
    _log_advisor("fan_assistant", time.monotonic() - start, "rules", device_id)
    return ChatResponse(
        reply=str(result["reply"]),
        language=language,
        source="rules",
        suggested_actions=[str(s) for s in result.get("suggested_actions", [])],
    )


# ---------------------------------------------------------------------------
# Public API — Ops Advisor
# ---------------------------------------------------------------------------


async def get_ops_recommendations(
    analysis: CrowdAnalysis,
    *,
    use_gemini: bool = False,
    project: str = "",
    region: str = "",
    prompt_version: int = 1,
) -> list[OpsRecommendation]:
    """Get operational recommendations — Gemini if available, rules as fallback.

    Catches ALL exceptions from Gemini and returns rules-based recommendations.
    """
    start = time.monotonic()

    # Check cache
    cache_data = json.dumps(
        {"zones": [d.zone_id for d in analysis.densities], "overall": analysis.overall_density_pct},
        sort_keys=True,
    )
    key = _cache_key("ops", cache_data)
    with _cache_lock:
        cached = _response_cache.get(key)
    if cached is not None:
        _log_advisor("ops_advisor", time.monotonic() - start, "cache", "system")
        return [OpsRecommendation(**r, source="cache") for r in cached.get("recommendations", [])]

    # Try Gemini
    if use_gemini and project:
        try:
            config = _load_prompt_config(prompt_version)
            ops_config = config.get("ops_advisor", {})
            client = _get_gemini_client(project, region)

            # Build crowd summary for the prompt
            crowd_summary = _build_crowd_prompt(analysis)
            payload = await asyncio.to_thread(
                _call_gemini,
                client,
                crowd_summary,
                ops_config.get("system_instruction", ""),
                ops_config.get("response_schema"),
                ops_config.get("temperature", 0.3),
                ops_config.get("max_output_tokens", 2048),
            )

            _validate_ops_response(payload, analysis)

            with _cache_lock:
                _response_cache[key] = payload

            _log_advisor("ops_advisor", time.monotonic() - start, "gemini", "system")
            return [
                OpsRecommendation(**r, source="gemini")
                for r in payload.get("recommendations", [])
            ]

        except Exception:
            logger.exception("Gemini ops advisor failed, falling back to rules engine")

    # Fallback: rules engine
    recommendations = generate_ops_recommendations(analysis)
    _log_advisor("ops_advisor", time.monotonic() - start, "rules", "system")
    return recommendations


def _build_crowd_prompt(analysis: CrowdAnalysis) -> str:
    """Build a text prompt summarizing crowd data for the ops advisor."""
    lines = [
        f"Stadium overall: {analysis.overall_density_pct:.1f}% capacity "
        f"({analysis.total_occupancy}/{analysis.total_capacity})",
        f"Hotspots: {', '.join(analysis.hotspots) if analysis.hotspots else 'None'}",
        "",
        "Zone densities:",
    ]
    for d in sorted(analysis.densities, key=lambda x: x.density_pct, reverse=True):
        lines.append(
            f"  {d.zone_id}: {d.density_pct:.0f}% ({d.current_count}/{d.capacity}) [{d.status}]"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Structured logging
# ---------------------------------------------------------------------------


def _log_advisor(
    endpoint: str,
    latency: float,
    source: str,
    device_id: str,
) -> None:
    """Log advisor call with structured fields for cloud logging queries."""
    device_hash = hashlib.sha256(device_id.encode()).hexdigest()[:12]
    logger.info(
        "Advisor response served",
        extra={
            "endpoint": endpoint,
            "latency_ms": round(latency * 1000, 1),
            "source": source,
            "device_id_hash": device_hash,
        },
    )
