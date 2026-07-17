"""MatchDay Command Center — FastAPI application entry point.

Assembles all route modules, middleware (CORS, body-size limiter, security
headers), structured logging, and static file serving for the frontend build.
"""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded

from app.config import get_settings
from app.rate_limit import limiter
from app.routes import chat, crowd, health, ops

# ---------------------------------------------------------------------------
# Structured logging configuration
# ---------------------------------------------------------------------------


def _configure_logging() -> None:
    """Set up JSON-structured logging for cloud environments."""
    try:
        from pythonjsonlogger.json import JsonFormatter

        handler = logging.StreamHandler()
        formatter = JsonFormatter(
            fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
            rename_fields={"asctime": "timestamp", "levelname": "severity"},
        )
        handler.setFormatter(formatter)
        logging.root.handlers = [handler]
        logging.root.setLevel(logging.INFO)
    except ImportError:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


_configure_logging()
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Security headers — applied to every response
# ---------------------------------------------------------------------------

_SECURITY_HEADERS: dict[str, str] = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "connect-src 'self'; "
        "img-src 'self' data:; "
        "frame-ancestors 'none'"
    ),
}

# ---------------------------------------------------------------------------
# Body size limit — 64 KB, checked BEFORE JSON parsing
# ---------------------------------------------------------------------------

_MAX_BODY_BYTES = 65_536  # 64 KB


# ---------------------------------------------------------------------------
# FastAPI app assembly
# ---------------------------------------------------------------------------


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="MatchDay Command Center",
        description="GenAI-powered FIFA World Cup 2026 smart stadium operations",
        version="1.0.0",
    )

    # --- Rate limiter ---
    app.state.limiter = limiter

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
        """Return 429 with Retry-After header — generic message, no internals."""
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Please try again shortly."},
            headers={"Retry-After": "60"},
        )

    # --- CORS ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Security headers middleware ---
    @app.middleware("http")
    async def security_headers(request: Request, call_next: object) -> Response:
        """Add security headers to every response."""
        response: Response = await call_next(request)  # type: ignore[misc]
        for header, value in _SECURITY_HEADERS.items():
            response.headers.setdefault(header, value)
        return response

    # --- Body size limiter middleware ---
    @app.middleware("http")
    async def body_size_limiter(request: Request, call_next: object) -> Response:
        """Reject oversized POST bodies before JSON parsing.

        Two-layer check (defense in depth):
        1. Fast path — check Content-Length header.
        2. Trust-nothing path — stream actual bytes to catch clients
           that omit or forge the Content-Length header.
        """
        if request.method in ("POST", "PUT", "PATCH"):
            # Fast path: check Content-Length header
            content_length = request.headers.get("content-length")
            if content_length is not None:
                try:
                    if int(content_length) > _MAX_BODY_BYTES:
                        return JSONResponse(
                            status_code=413,
                            content={"detail": "Request body too large"},
                        )
                except ValueError:
                    return JSONResponse(
                        status_code=400,
                        content={"detail": "Invalid Content-Length header"},
                    )

            # Trust-nothing path: stream actual bytes regardless of header
            body = await request.body()
            if len(body) > _MAX_BODY_BYTES:
                return JSONResponse(
                    status_code=413,
                    content={"detail": "Request body too large"},
                )

        return await call_next(request)  # type: ignore[misc]

    # --- Routes ---
    app.include_router(health.router)
    app.include_router(chat.router)
    app.include_router(crowd.router)
    app.include_router(ops.router)

    # --- Static file serving for frontend build ---
    static_path = Path(__file__).parent.parent / "static"
    if static_path.is_dir():
        app.mount("/", StaticFiles(directory=str(static_path), html=True), name="static")

    logger.info(
        "MatchDay Command Center started",
        extra={
            "gemini_enabled": settings.use_gemini,
            "firestore_enabled": settings.use_firestore,
        },
    )

    return app


app = create_app()
