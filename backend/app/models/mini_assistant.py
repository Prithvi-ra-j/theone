"""Mini Assistant models for Dristhi."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class MiniAssistant(Base):
    """Mini Assistant model for storing user's assistant preferences."""
    
    __tablename__ = "mini_assistants"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    avatar = Column(String(100), nullable=False)  # Path or identifier for avatar image
    personality = Column(String(50), nullable=False)  # e.g., "friendly", "professional", "motivational"
    color_theme = Column(String(50), nullable=True)  # User's preferred color theme for the assistant
    greeting_message = Column(Text, nullable=True)  # Custom greeting message
    preferences = Column(JSONB, nullable=True)  # Additional customization options
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="mini_assistant")
    interactions = relationship("AssistantInteraction", back_populates="assistant", cascade="all, delete-orphan")


class AssistantInteraction(Base):
    """Model for storing interactions with the Mini Assistant."""
    
    __tablename__ = "assistant_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    assistant_id = Column(Integer, ForeignKey("mini_assistants.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    interaction_type = Column(String(50), nullable=False)  # e.g., "greeting", "reminder", "suggestion"
    content = Column(Text, nullable=False)
    interaction_metadata = Column(JSONB, nullable=True)  # Additional data about the interaction
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    assistant = relationship("MiniAssistant", back_populates="interactions")
    user = relationship("User")