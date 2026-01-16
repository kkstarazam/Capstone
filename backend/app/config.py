"""Application configuration settings."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App settings
    app_name: str = "Weather Intelligence Agent"
    debug: bool = False

    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Letta settings
    letta_base_url: Optional[str] = None  # Uses default if not set

    # Google Calendar OAuth (optional, for calendar integration)
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None

    # Open-Meteo doesn't require API key - it's free!

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
