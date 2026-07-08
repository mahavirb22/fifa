# MatchDay Command Center — Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         CLIENT (Browser)                               │
│  ┌──────────────────┐  ┌───────────────────┐  ┌────────────────────┐  │
│  │  Fan Assistant    │  │  Crowd Heatmap    │  │  Ops Dashboard     │  │
│  │  (Chat + i18n)   │  │  (Live density)   │  │  (AI recs + logs)  │  │
│  └──────┬───────────┘  └──────┬────────────┘  └───────┬────────────┘  │
│         │    React + TypeScript (Vite)                 │               │
├─────────┼─────────────────────┼────────────────────────┼───────────────┤
│         │          /api/*     │                        │               │
│         ▼                     ▼                        ▼               │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    FastAPI Application                           │  │
│  │  ┌─────────┐  ┌──────────────┐  ┌───────────┐  ┌────────────┐  │  │
│  │  │ /chat   │  │ /crowd/*     │  │ /ops/*    │  │ /health    │  │  │
│  │  │ (AI)    │  │ (density)    │  │ (actions) │  │ (status)   │  │  │
│  │  └────┬────┘  └──────┬───────┘  └─────┬─────┘  └────────────┘  │  │
│  │       │              │                 │                         │  │
│  │  ┌────▼────┐    ┌────▼──────┐   ┌─────▼──────┐                 │  │
│  │  │ Advisor │    │ Crowd     │   │ Repository │                 │  │
│  │  │ Gemini  │    │ Simulator │   │ Protocol   │                 │  │
│  │  │ ↓Rules  │    │ (pure)    │   │ ↓Firestore │                 │  │
│  │  └────┬────┘    └───────────┘   │ ↓Memory    │                 │  │
│  │       │                         └────────────┘                  │  │
│  └───────┼─────────────────────────────────────────────────────────┘  │
│          ▼                                                            │
│  ┌──────────────┐  ┌──────────────────┐                              │
│  │ Gemini API   │  │ Cloud Firestore  │                              │
│  │ (Vertex AI)  │  │ (Persistence)    │                              │
│  └──────────────┘  └──────────────────┘                              │
└─────────────────────────────────────────────────────────────────────────┘
```

## Layer Responsibilities

| Layer | Module(s) | Rule |
|-------|-----------|------|
| **Domain** | `stadium/zones.py`, `stadium/constants.py`, `crowd/simulator.py` | No I/O — pure functions only. Same input → same output. |
| **Intelligence** | `advisor/gemini.py`, `advisor/rules.py`, `advisor/prompts/` | Graceful degradation: Gemini → rules fallback. Every response tagged with source. |
| **Persistence** | `repository/base.py`, `firestore_repo.py`, `memory_repo.py` | Protocol interface. DI selects implementation. Routes never import concrete classes. |
| **Transport** | `routes/chat.py`, `routes/crowd.py`, `routes/ops.py`, `routes/health.py` | Thin handlers. Depend on abstractions. Rate-limit only expensive endpoints. |
| **Composition** | `main.py`, `config.py`, `deps.py`, `rate_limit.py` | Wiring only — no business logic. Config validated at startup via Pydantic. |

## Design Rules

- **Reliability-First**: Gemini provides the richest responses, but the rules engine is always available. The system never fails to serve a response.
- **Graceful Degradation**: Every external dependency (Gemini, Firestore) has a full-featured fallback. Responses are tagged with their source (`"gemini"`, `"rules"`, `"cache"`).
- **Inward Dependencies**: Transport → Domain → Models. Domain layer imports nothing from routes or framework code.
- **Privacy by Design**: Anonymous device IDs only. No PII collected. Device IDs hashed before logging.

## Frontend Structure

| Component | Purpose | Hook |
|-----------|---------|------|
| `FanAssistant` | Multilingual chat interface | `useStadiumChat` |
| `CrowdHeatmap` | Live zone density visualization | `useCrowdData` |
| `OpsPanel` | AI recommendations + action logging | `useOpsActions` |
| `VenueNavigator` | Accessibility-aware wayfinding | (local state) |
| `LanguageSelector` | 12-language picker | (controlled by parent) |
| `AlertBadge` | Severity indicator (text + color) | (stateless) |

## Quality Gates

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the full quality gates table.
