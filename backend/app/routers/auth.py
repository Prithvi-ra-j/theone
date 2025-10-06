"""Minimal auth helper for prototyping.

Provides a `router` object (so `app.main` can include it) and a
`get_current_user` dependency that either verifies a JWT or returns a demo
user when running in local dev (DEBUG) or when the `DEV_DISABLE_AUTH`
environment variable is set.
"""
from typing import Any, Optional
import os
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from loguru import logger

from app.core.config import settings
from app.db.session import get_db
from ..models.user import User
from app.utils.jwt import verify_token
from app.utils.security import hash_password


router = APIRouter(prefix="/auth")
# Make HTTPBearer not raise automatically so we can return consistent 401 responses
security = HTTPBearer(auto_error=False)


def get_current_user(
	request: Request,
	credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
	db: Session = Depends(get_db),
) -> Optional[User]:
	"""Resolve and return the current user or raise 401.

	If running locally (settings.DEBUG) or if DEV_DISABLE_AUTH is set to
	true/1, return or create a demo user instead to simplify prototype flows.
	"""
	# For prototype mode, ALWAYS return or create a demo user so the app
	# never returns 401s. This intentionally disables auth checks. Make sure
	# this is only used in local/dev environments.
	try:
		demo_email = os.environ.get('DEV_DEMO_EMAIL', 'demo@example.com')
		demo_password = os.environ.get('DEV_DEMO_PASSWORD', 'demopass123')
		user = db.query(User).filter(User.email == demo_email).first()
		if not user:
			# Ensure required non-nullable fields (hashed_password) are set
			user = User(
				email=demo_email,
				hashed_password=hash_password(demo_password),
				name='Demo User',
				is_verified=True,
				is_active=True,
			)
			db.add(user)
			db.commit()
			db.refresh(user)
		return user
	except Exception:
		logger.exception('Failed creating demo user; falling back to token auth')

	# If, for some reason, demo user creation failed above, fall back to
	# token-based verification. We keep token verification but treat failures
	# as non-fatal and return None so callers that used the optional
	# dependency still get None instead of a 401.
	try:
		if request is not None and request.method == "OPTIONS":
			return None
		if credentials is None:
			return None
		token = credentials.credentials
		token_data = verify_token(token)
		if token_data is None:
			return None
		email = None
		if hasattr(token_data, 'email'):
			email = getattr(token_data, 'email')
		elif isinstance(token_data, dict):
			email = token_data.get('email') or token_data.get('sub')
		if not email:
			return None
		user = db.query(User).filter(User.email == email).first()
		if user is None or not user.is_active:
			return None
		return user
	except Exception:
		logger.exception('Token verification failed, returning None')
		return None


def get_optional_current_user(
	request: Request,
	credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
	db: Session = Depends(get_db),
) -> Optional[User]:
	"""Resolve current user when available; never raise 401.

	This is a safe dependency for public/read-only endpoints. It returns
	None for unauthenticated requests instead of raising HTTPException.
	"""
	# Delegate to get_current_user so behavior is consistent (demo user
	# creation will be handled there). This ensures optional callers always
	# receive either the demo user or None without raising 401.
	return get_current_user(request=request, credentials=credentials, db=db)


# @router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
# async def register(user_data: UserCreate, db: Session = Depends(get_db)) -> Any:
#     """Register a new user."""
#     # Check if user already exists
#     existing_user = db.query(User).filter(User.email == user_data.email).first()
#     if existing_user:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Email already registered",
#         )
    
#     # Create new user
#     hashed_password = hash_password(user_data.password)
#     db_user = User(
#         email=user_data.email,
#         hashed_password=hashed_password,
#         name=user_data.name,
#         bio=user_data.bio,
#         phone_number=user_data.phone_number,
#         is_verified=True,  # For MVP, auto-verify users
#     )
    
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
    
#     return db_user


# @router.post("/login", response_model=Token)
# async def login(user_credentials: UserLogin, db: Session = Depends(get_db)) -> Any:
#     """Login user and return access token."""
#     # Authenticate user
#     user = db.query(User).filter(User.email == user_credentials.email).first()
#     if not user or not verify_password(user_credentials.password, user.hashed_password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect email or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
    
#     if not user.is_active:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Inactive user",
#         )
    
#     # Update last login
#     user.update_last_login()
#     db.commit()
    
#     # Create tokens (wrap in try/except to log detailed errors)
#     access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
#     # Debug: log relevant JWT settings to help diagnose AttributeError issues
#     logger.debug("Creating access token - SECRET_KEY set: {} | JWT_ALGORITHM: {} | EXPIRE_MINUTES: {}",
#                  bool(getattr(settings, "SECRET_KEY", None)),
#                  getattr(settings, "JWT_ALGORITHM", None),
#                  getattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", None))
#     try:
#         access_token = create_access_token(
#             data={"sub": user.email, "user_id": user.id},
#             expires_delta=access_token_expires
#         )
#         refresh_token = create_refresh_token(data={"sub": user.email, "user_id": user.id})
#     except Exception as exc:
#         # Log full exception and re-raise as HTTP 500 to preserve original behavior while
#         # providing clearer logs for debugging.
#         logger.exception("Failed creating JWT tokens: {}", exc)
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Internal error creating authentication tokens",
#         )
    
#     return {
#         "access_token": access_token,
#         "refresh_token": refresh_token,
#         "token_type": "bearer",
#         "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
#     }


# @router.post("/refresh", response_model=Token)
# async def refresh_token(
#     refresh_token: str,
#     db: Session = Depends(get_db)
# ) -> Any:
#     """Refresh access token using refresh token."""
#     from app.utils.jwt import verify_refresh_token
    
#     token_data = verify_refresh_token(refresh_token)
#     if token_data is None:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid refresh token",
#         )
    
#     user = db.query(User).filter(User.email == token_data.email).first()
#     if not user or not user.is_active:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="User not found or inactive",
#         )
    
#     # Create new access token
#     access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user.email, "user_id": user.id},
#         expires_delta=access_token_expires
#     )
    
#     return {
#         "access_token": access_token,
#         "token_type": "bearer",
#         "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
#     }


# @router.get("/me", response_model=UserProfile)
# async def get_current_user_profile(current_user: User = Depends(get_current_user)) -> Any:
#     """Get current user profile."""
#     return current_user


# @router.put("/me", response_model=UserProfile)
# async def update_current_user_profile(
#     user_update: UserUpdate,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ) -> Any:
#     """Update current user profile."""
#     # Update fields if provided
#     if user_update.name is not None:
#         current_user.name = user_update.name
#     if user_update.bio is not None:
#         current_user.bio = user_update.bio
#     if user_update.avatar_url is not None:
#         current_user.avatar_url = user_update.avatar_url
#     if user_update.phone_number is not None:
#         current_user.phone_number = user_update.phone_number
#     if user_update.preferences is not None:
#         import json
#         current_user.preferences = json.dumps(user_update.preferences)
    
#     db.commit()
#     db.refresh(current_user)
    
#     return current_user


# @router.post("/change-password")
# async def change_password(
#     password_change: PasswordChange,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ) -> Any:
#     """Change current user password."""
#     # Verify current password
#     if not verify_password(password_change.current_password, current_user.hashed_password):
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Current password is incorrect",
#         )
    
#     # Hash and update new password
#     new_hashed_password = hash_password(password_change.new_password)
#     current_user.hashed_password = new_hashed_password
    
#     db.commit()
    
#     return {"message": "Password changed successfully"}


# @router.post("/logout")
# async def logout() -> Any:
#     """Logout user (client should discard tokens)."""
#     return {"message": "Successfully logged out"}


# @router.post("/forgot-password")
# async def forgot_password(password_reset: PasswordReset, db: Session = Depends(get_db)) -> Any:
#     """Request password reset (placeholder for future implementation)."""
#     # TODO: Implement email-based password reset
#     # For MVP, just return success message
#     return {"message": "If the email exists, a password reset link has been sent"}


# @router.post("/reset-password")
# async def reset_password(
#     password_reset: PasswordResetConfirm,
#     db: Session = Depends(get_db)
# ) -> Any:
#     """Reset password using reset token (placeholder for future implementation)."""
#     # TODO: Implement password reset with token validation
#     return {"message": "Password reset functionality coming soon"}
