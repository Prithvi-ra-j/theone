"""Mini Assistant router for managing user's personalized assistant."""

from typing import Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.mini_assistant import MiniAssistant, AssistantInteraction
from app.routers.auth import get_current_user, get_optional_current_user
from pydantic import BaseModel, Field

router = APIRouter()


# Pydantic models for request/response
class MiniAssistantBase(BaseModel):
    name: str
    avatar: str
    personality: str
    color_theme: Optional[str] = None
    greeting_message: Optional[str] = None
    preferences: Optional[dict] = None


class MiniAssistantCreate(MiniAssistantBase):
    pass


class MiniAssistantUpdate(MiniAssistantBase):
    pass


class MiniAssistantRead(MiniAssistantBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class InteractionBase(BaseModel):
    interaction_type: str
    content: str
    metadata: Optional[dict] = None


class InteractionCreate(InteractionBase):
    pass


class InteractionRead(InteractionBase):
    id: int
    assistant_id: int
    user_id: int
    is_read: bool
    created_at: datetime

    class Config:
        orm_mode = True


# API Endpoints
@router.post("/mini-assistant", response_model=MiniAssistantRead)
async def create_mini_assistant(
    assistant: MiniAssistantCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new mini assistant for the current user."""
    # Check if user already has an assistant
    existing = db.query(MiniAssistant).filter(
        MiniAssistant.user_id == current_user.id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a mini assistant"
        )
    
    # Create new assistant
    db_assistant = MiniAssistant(
        user_id=current_user.id,
        name=assistant.name,
        avatar=assistant.avatar,
        personality=assistant.personality,
        color_theme=assistant.color_theme,
        greeting_message=assistant.greeting_message,
        preferences=assistant.preferences
    )
    
    db.add(db_assistant)
    db.commit()
    db.refresh(db_assistant)
    
    # Create initial greeting interaction
    greeting = f"Hello {current_user.name}! I'm {assistant.name}, your personal assistant. I'm here to help you achieve your goals."
    
    interaction = AssistantInteraction(
        assistant_id=db_assistant.id,
        user_id=current_user.id,
        interaction_type="greeting",
        content=greeting
    )
    
    db.add(interaction)
    db.commit()
    
    return db_assistant


@router.get("/mini-assistant", response_model=MiniAssistantRead)
async def get_mini_assistant(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get the current user's mini assistant."""
    assistant = db.query(MiniAssistant).filter(
        MiniAssistant.user_id == current_user.id
    ).first()
    
    if not assistant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mini assistant not found"
        )
    
    return assistant


@router.put("/mini-assistant", response_model=MiniAssistantRead)
async def update_mini_assistant(
    assistant: MiniAssistantUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update the current user's mini assistant."""
    db_assistant = db.query(MiniAssistant).filter(
        MiniAssistant.user_id == current_user.id
    ).first()
    
    if not db_assistant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mini assistant not found"
        )
    
    # Update fields
    db_assistant.name = assistant.name
    db_assistant.avatar = assistant.avatar
    db_assistant.personality = assistant.personality
    db_assistant.color_theme = assistant.color_theme
    db_assistant.greeting_message = assistant.greeting_message
    db_assistant.preferences = assistant.preferences
    db_assistant.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_assistant)
    
    return db_assistant


@router.post("/mini-assistant/interactions", response_model=InteractionRead)
async def create_interaction(
    interaction: InteractionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new interaction with the mini assistant."""
    # Get user's assistant
    assistant = db.query(MiniAssistant).filter(
        MiniAssistant.user_id == current_user.id
    ).first()
    
    if not assistant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mini assistant not found"
        )
    
    # Create interaction
    db_interaction = AssistantInteraction(
        assistant_id=assistant.id,
        user_id=current_user.id,
        interaction_type=interaction.interaction_type,
        content=interaction.content,
        metadata=interaction.metadata
    )
    
    db.add(db_interaction)
    db.commit()
    db.refresh(db_interaction)
    
    return db_interaction


@router.get("/mini-assistant/interactions", response_model=List[InteractionRead])
async def get_interactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 10,
    offset: int = 0
) -> Any:
    """Get the current user's interactions with their mini assistant."""
    # Get user's assistant
    assistant = db.query(MiniAssistant).filter(
        MiniAssistant.user_id == current_user.id
    ).first()
    
    if not assistant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mini assistant not found"
        )
    
    # Get interactions
    interactions = db.query(AssistantInteraction).filter(
        AssistantInteraction.user_id == current_user.id,
        AssistantInteraction.assistant_id == assistant.id
    ).order_by(AssistantInteraction.created_at.desc()).offset(offset).limit(limit).all()
    
    return interactions


@router.put("/mini-assistant/interactions/{interaction_id}/read")
async def mark_interaction_as_read(
    interaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Mark an interaction as read."""
    interaction = db.query(AssistantInteraction).filter(
        AssistantInteraction.id == interaction_id,
        AssistantInteraction.user_id == current_user.id
    ).first()
    
    if not interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interaction not found"
        )
    
    interaction.is_read = True
    db.commit()
    
    return {"status": "success"}