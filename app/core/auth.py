"""Authentication and authorization utilities."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.config import settings

logger = logging.getLogger(__name__)
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    
    jwt_secret = settings.jwt_secret or settings.secret_key
    encoded_jwt = jwt.encode(to_encode, jwt_secret, algorithm=settings.jwt_algorithm)
    return encoded_jwt


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify and decode JWT token."""
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        jwt_secret = settings.jwt_secret or settings.secret_key
        payload = jwt.decode(token, jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError:
        raise credentials_exception


async def get_current_user(token: dict = Depends(verify_token)) -> dict:
    """Get current user from token."""
    user_id = token.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return {"user_id": user_id, **token}

