"""Application configuration loaded via pydantic-settings.

All values come from environment variables or a .env file. No secret values
live here — credentials come from Application Default Credentials (ADC).
The Settings object is cached as a process-lifetime singleton via @lru_cache.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated application settings — fails fast on missing/invalid values."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Google Cloud
    gcp_project_id: str = "matchday-dev"
    gcp_region: str = "us-central1"

    # Feature flags
    use_gemini: bool = False
    use_firestore: bool = False

    # Prompt versioning
    gemini_prompt_version: int = 1

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # Rate limiting
    rate_limit_storage: str = "memory://"

    def get_cors_origins(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the singleton Settings instance, cached for the process lifetime."""
    return Settings()
