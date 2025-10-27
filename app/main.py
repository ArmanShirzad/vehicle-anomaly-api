"""Main FastAPI application."""

import logging
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from app.api.routes import health, ingest, score
from app.config import settings
from app.core.auth import verify_token
from app.core.database import close_database, init_database
from app.core.metrics import setup_metrics
from app.core.rate_limit import RateLimitMiddleware
from app.instrumentation import init_tracing

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")

    # Initialize database
    init_database()

    # Initialize Sentry if DSN is provided
    if settings.sentry_dsn:
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            integrations=[
                FastApiIntegration(auto_enabling_instrumentations=False),
                LoggingIntegration(level=logging.INFO),
            ],
            traces_sample_rate=0.1,
            environment=settings.environment,
        )

    yield

    # Shutdown
    logger.info("Shutting down")
    
    # Close database connections
    await close_database()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

# Add rate limiting middleware
if settings.rate_limit_enabled:
    app.add_middleware(RateLimitMiddleware, calls=settings.rate_limit_per_minute, period=60)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins if settings.cors_origins else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Add security middleware
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=["*"] if settings.debug else ["localhost", "127.0.0.1"]
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests."""
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response


# Observability hooks
init_tracing(app)
setup_metrics(app)
logger.info("OpenTelemetry tracing and Prometheus metrics enabled")

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(ingest.router, tags=["telemetry"])
app.include_router(score.router, tags=["telemetry"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "environment": settings.environment,
    }

