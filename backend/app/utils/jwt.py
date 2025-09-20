"""JWT utilities for authentication."""

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from loguru import logger

from app.core.config import settings
from app.schemas.user import TokenData


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a new JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Increasing token expiration time to avoid frequent expirations
        expire = datetime.utcnow() + timedelta(days=7)  # Set to 7 days instead of minutes
    
    to_encode.update({"exp": expire})
    # Support legacy or misnamed env var 'ALGORITHM' by falling back if JWT_ALGORITHM missing
    alg = getattr(settings, "JWT_ALGORITHM", None) or getattr(settings, "ALGORITHM", "HS256")
    logger.debug("Encoding access token using algorithm: {}", alg)
    try:
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=alg)
    except Exception as e:
        logger.exception("Failed to encode JWT: {}", e)
        raise

    logger.debug(f"Created access token for user {data.get('sub', 'unknown')}")
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create a new JWT refresh token."""
    to_encode = data.copy()
    
    # Refresh tokens last longer
    expire = datetime.utcnow() + timedelta(days=30)  # Set to 30 days for refresh tokens
    to_encode.update({"exp": expire, "type": "refresh"})
    
    alg = getattr(settings, "JWT_ALGORITHM", None) or getattr(settings, "ALGORITHM", "HS256")
    logger.debug("Encoding refresh token using algorithm: {}", alg)
    try:
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=alg)
    except Exception as e:
        logger.exception("Failed to encode refresh JWT: {}", e)
        raise

    logger.debug(f"Created refresh token for user {data.get('sub', 'unknown')}")
    return encoded_jwt


def verify_token(token: str) -> Optional[TokenData]:
    """Verify and decode a JWT token."""
    try:
        alg = getattr(settings, "JWT_ALGORITHM", None) or getattr(settings, "ALGORITHM", "HS256")
        logger.debug("Decoding token using algorithm(s): {}", alg)
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[alg])
        email: str = payload.get("sub")
        user_id: int = payload.get("user_id")

        if email is None:
            logger.warning("Token verification failed: missing email")
            return None

        token_data = TokenData(email=email, user_id=user_id)
        logger.debug(f"Token verified for user {email}")
        return token_data

    except JWTError as e:
        logger.warning(f"Token verification failed: {e}")
        return None


def verify_refresh_token(token: str) -> Optional[TokenData]:
    """Verify and decode a JWT refresh token."""
    try:
        alg = getattr(settings, "JWT_ALGORITHM", None) or getattr(settings, "ALGORITHM", "HS256")
        logger.debug("Decoding refresh token using algorithm(s): {}", alg)
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[alg])

        # Check if it's a refresh token
        token_type = payload.get("type")
        if token_type != "refresh":
            logger.warning("Invalid token type for refresh")
            return None

        email: str = payload.get("sub")
        user_id: int = payload.get("user_id")

        if email is None:
            logger.warning("Refresh token verification failed: missing email")
            return None

        token_data = TokenData(email=email, user_id=user_id)
        logger.debug(f"Refresh token verified for user {email}")
        return token_data

    except JWTError as e:
        logger.warning(f"Refresh token verification failed: {e}")
        return None


def get_token_expiration(token: str) -> Optional[datetime]:
    """Get the expiration time of a JWT token."""
    try:
        alg = getattr(settings, "JWT_ALGORITHM", None) or getattr(settings, "ALGORITHM", "HS256")
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[alg])
        exp_timestamp = payload.get("exp")

        if exp_timestamp:
            return datetime.fromtimestamp(exp_timestamp)

        return None

    except JWTError:
        return None


def is_token_expired(token: str) -> bool:
    """Check if a JWT token is expired."""
    exp_time = get_token_expiration(token)
    
    if exp_time is None:
        return True
    
    return datetime.utcnow() >= exp_time
