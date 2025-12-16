"""
Configuration management for the Nonprofit CRM application.
"""
import os
from typing import Optional, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "Nonprofit CRM"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./nonprofit_crm.db"

    # Supabase
    NEXT_PUBLIC_SUPABASE_URL: Optional[str] = None
    NEXT_PUBLIC_SUPABASE_ANON_KEY: Optional[str] = None

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"  # Change this!
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # API
    API_V1_PREFIX: str = "/api/v1"
    OPENVOICE_ENABLED: bool = False
    OPENVOICE_SERVER_URL: Optional[str] = None
    OPENVOICE_SPEAKER_ID: Optional[str] = "default"
    OPENVOICE_TIMEOUT_SECONDS: int = 45
    OPENVOICE_MAX_CHARS: int = 220

    # Anthropic / AI configuration
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"
    VOICE_AGENT_CONFIDENCE_THRESHOLD: float = 0.65

    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from string or list."""
        if isinstance(v, str):
            # Handle comma-separated string
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        elif isinstance(v, list):
            return v
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra='ignore'
    )


# Global settings instance
settings = Settings()
