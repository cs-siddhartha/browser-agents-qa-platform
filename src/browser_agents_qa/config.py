from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


# Keep environment parsing behind one typed model so later services do not read
# environment variables independently or interpret the same setting differently.
class Settings(BaseSettings):
    """Centralizes runtime configuration so services use one validated source."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="BROWSER_AGENTS_QA_",
        extra="ignore",
        frozen=True,
    )

    app_name: str = "Browser Agents QA API"
    environment: str = "development"
    api_prefix: str = "/api/v1"


# Cache validated configuration because it is immutable for the process lifetime
# and every request should observe the same application settings.
@lru_cache
def get_settings() -> Settings:
    """Return the process-wide validated application settings."""

    return Settings()
