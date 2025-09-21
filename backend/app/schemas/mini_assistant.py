"""Schemas for Mini Assistant."""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel


class MiniAssistantBase(BaseModel):
    """Base schema for Mini Assistant."""
    name: str
    avatar: str
    personality: str
    color_theme: Optional[str] = None
    greeting_message: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class MiniAssistantCreate(MiniAssistantBase):
    """Schema for creating a Mini Assistant."""
    pass


class MiniAssistantUpdate(BaseModel):
    """Schema for updating a Mini Assistant."""
    name: Optional[str] = None
    avatar: Optional[str] = None
    personality: Optional[str] = None
    color_theme: Optional[str] = None
    greeting_message: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class MiniAssistantResponse(MiniAssistantBase):
    """Schema for Mini Assistant response."""
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class AssistantInteractionBase(BaseModel):
    """Base schema for Assistant Interaction."""
    interaction_type: str
    content: str
    metadata: Optional[Dict[str, Any]] = None


class AssistantInteractionCreate(AssistantInteractionBase):
    """Schema for creating an Assistant Interaction."""
    pass


class AssistantInteractionResponse(AssistantInteractionBase):
    """Schema for Assistant Interaction response."""
    id: int
    assistant_id: int
    user_id: int
    is_read: bool
    created_at: datetime

    class Config:
        orm_mode = True