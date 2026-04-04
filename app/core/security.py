from datetime import datetime, timedelta, timezone
from typing import Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a plain text password using bcrypt. Truncates to 72 bytes (bcrypt limit)."""
    return pwd_context.hash(password[:72])

def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain text password against a bcrypt hash."""
    return pwd_context.verify(plain[:72], hashed)

def create_access_token(subject: str | int, extra: dict[str, Any] = {}) -> str:
    """Create a short-lived JWT access token for the given subject."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": str(subject), "exp": expire, "type": "access", **extra}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.algorithm)

def create_refresh_token(subject: str | int) -> str:
    """Create a long-lived JWT refresh token for the given subject."""
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    payload = {"sub": str(subject), "exp": expire, "type": "refresh"}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.algorithm)

def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT token. Raises ValueError if invalid or expired."""
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.algorithm])
    except JWTError:
        raise ValueError("Invalid or expired token")