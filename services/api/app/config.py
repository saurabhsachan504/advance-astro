from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_name: str = "Advance Astro API"
    api_prefix: str = "/v1"
    allowed_origins: str = "http://localhost:3000"
    ephemeris_path: Path = Path("/app/data/ephemeris")
    engine_version: str = "0.1.0"
    max_upload_bytes: int = Field(default=10 * 1024 * 1024)
    image_retention_hours: int = 1

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

@lru_cache
def get_settings() -> Settings:
    return Settings()

