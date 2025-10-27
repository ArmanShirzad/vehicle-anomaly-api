"""Application configuration."""

import secrets

from pydantic_settings import BaseSettings
from pydantic_settings import ConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "FastAPI Template"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    # Database
    database_url: str | None = None

    # Security
    secret_key: str = ""  # Will be generated if empty
    cors_origins: list[str] = []  # Empty by default for security

    # Sentry
    sentry_dsn: str | None = None

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    model_artifact_dir: str = "artifacts"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Generate a random secret key if not provided
        if not self.secret_key:
            self.secret_key = secrets.token_urlsafe(32)

    model_config = ConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()

