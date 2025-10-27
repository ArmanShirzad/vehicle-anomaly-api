"""Application configuration."""

import secrets

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


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
    jwt_secret: str = ""  # JWT secret for authentication
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Storage
    s3_bucket_name: str = ""  # S3 bucket for model storage
    aws_region: str = "us-east-1"
    use_local_storage: bool = True  # Use local storage if True, S3 if False
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 60

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

