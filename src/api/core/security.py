"""Security utilities."""

import secrets
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt

from app.config import settings


def create_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[dict] = None,
) -> str:
    """Create a JWT token."""
    to_encode = {"sub": subject, "iat": datetime.utcnow()}
    if expires_delta:
        to_encode["exp"] = datetime.utcnow() + expires_delta
    if additional_claims:
        to_encode.update(additional_claims)
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    """Decode a JWT token."""
    return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])


def generate_api_key() -> str:
    """Generate a secure API key."""
    return secrets.token_urlsafe(32)


def verify_api_key(key: str) -> bool:
    """Verify an API key."""
    # In production, verify against stored keys
    return len(key) >= 32
