"""Users router exposing profile update including assistant customization fields."""

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.user import UserUpdate, UserProfile


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserProfile)
async def get_me(current_user: User = Depends(get_current_user)) -> Any:
    """Return current user's profile."""
    return current_user


@router.put("/me", response_model=UserProfile)
async def update_me(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Update current user's profile including assistant fields."""
    data = payload.model_dump(exclude_unset=True)
    # Preferences is a JSON dict stored as text in the ORM model using helper methods
    preferences = data.pop("preferences", None)

    for field, value in data.items():
        setattr(current_user, field, value)

    if preferences is not None:
        try:
            current_user.set_preferences(preferences)
        except Exception:
            # Fallback assign raw if helper not available in runtime
            import json as _json
            current_user.preferences = _json.dumps(preferences)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user
