"""Rate limiting middleware."""

import time
from collections import defaultdict
from typing import Callable

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings

logger = None


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""

    def __init__(self, app, calls: int = 60, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        
        # Skip rate limiting for health checks
        if request.url.path.startswith(("/health", "/healthz", "/metrics")):
            return await call_next(request)

        if not settings.rate_limit_enabled:
            return await call_next(request)

        # Get client identifier
        client_ip = request.client.host if request.client else "unknown"
        
        # Clean old entries
        current_time = time.time()
        self.clients[client_ip] = [
            timestamp
            for timestamp in self.clients[client_ip]
            if current_time - timestamp < self.period
        ]
        
        # Check rate limit
        if len(self.clients[client_ip]) >= self.calls:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": f"Rate limit exceeded: {self.calls} requests per {self.period} seconds"
                },
                headers={"Retry-After": str(self.period)},
            )
        
        # Add current request
        self.clients[client_ip].append(current_time)
        
        # Process request
        response = await call_next(request)
        return response

