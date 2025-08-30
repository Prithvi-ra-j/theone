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
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    logger.debug(f"Created access token for user {data.get('sub', 'unknown')}")
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create a new JWT refresh token."""
    to_encode = data.copy()
    
    # Refresh tokens last longer
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    logger.debug(f"Created refresh token for user {data.get('sub', 'unknown')}")
    return encoded_jwt


def verify_token(token: str) -> Optional[TokenData]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
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
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
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
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
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
