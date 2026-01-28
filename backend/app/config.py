"""Application configuration settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App settings
    app_name: str = "Weather Intelligence Agent"
    debug: bool = False

    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # CORS settings - comma-separated list of allowed origins
    # Example: "http://localhost:3000,https://myapp.com"
    cors_origins: str = "http://localhost:3000,http://localhost:8080"

    # Letta settings
    letta_base_url: Optional[str] = None  # Uses default if not set

    # Google Calendar OAuth (optional, for calendar integration)
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None

    # Open-Meteo doesn't require API key - it's free!

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Ignore extra fields in .env file
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        if not self.cors_origins:
            return []
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
