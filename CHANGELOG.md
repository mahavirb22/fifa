# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-07

### Added

- **Fan Assistant**: Multilingual AI chatbot supporting 12+ languages for wayfinding, food recommendations, accessibility services, medical stations, and transportation info
- **Crowd Heatmap**: Real-time zone density visualization with color-coded tiles and accessible data table equivalent
- **Operations Dashboard**: AI-powered operational recommendations with severity-tagged alerts and action logging
- **Venue Navigator**: Accessibility-aware wayfinding with elevator route option between MetLife Stadium zones
- **Gemini Integration**: Vertex AI-powered GenAI advisor with structured output schema, response validation, and TTL caching
- **Graceful Degradation**: Full-featured rules engine fallback when Gemini is unavailable — system never fails to serve
- **Repository Pattern**: Protocol-based persistence with Firestore and in-memory implementations, DI-selectable
- **Multilingual Support**: Template responses in 12 languages (EN, ES, FR, PT, AR, DE, JA, ZH, KO, HI, IT, NL)
- **WCAG AA Accessibility**: Semantic HTML, aria-labelledby, skip link, live regions, focus-visible, data table equivalents, reduced-motion support
- **Security**: ADC authentication (no API keys), body-size limiter, security headers (CSP, X-Frame-Options), rate limiting on AI endpoints, anonymous device IDs
- **Structured Logging**: JSON-formatted logs with first-class fields (endpoint, latency_ms, source, device_id_hash)
- **Docker**: Multi-stage build (Node + Python slim), non-root user, health check
- **CI Pipeline**: 4-job GitHub Actions (backend quality, frontend quality, E2E, API drift detection)
- **Test Suite**: 40+ backend tests (90%+ coverage), 20+ frontend tests with axe accessibility assertions on every component
- **Documentation**: README with rubric mapping, ARCHITECTURE.md with system diagram, CONTRIBUTING.md with quality gates
