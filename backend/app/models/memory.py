"""Memory models for AI-powered user context and conversation tracking."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Float, JSON, LargeBinary
from sqlalchemy.orm import relationship

from ..db.session import Base


class UserMemory(Base):
    """User memory storage for AI context and personalization."""
    
    __tablename__ = "usermemory"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    
    # Memory content
    content = Column(Text, nullable=False)  # the actual memory content
    memory_type = Column(String(50), nullable=False)  # preference, fact, goal, habit, insight, etc.
    category = Column(String(100), nullable=True)  # career, finance, health, personal, etc.
    
    # Context and metadata
    source = Column(String(100), nullable=True)  # conversation, habit_completion, mood_log, etc.
    confidence_score = Column(Float, default=1.0, nullable=False)  # 0-1 confidence in this memory
    
    # Relationships and references
    related_entity_type = Column(String(50), nullable=True)  # habit, goal, expense, etc.
    related_entity_id = Column(Integer, nullable=True)
    
    # Memory properties
    is_active = Column(Boolean, default=True, nullable=False)
    importance_score = Column(Float, default=0.5, nullable=False)  # 0-1 importance ranking
    
    # FAISS vector indexing
    vector_id = Column(Integer, nullable=True)  # ID in the FAISS index
    
    # Access tracking
    access_count = Column(Integer, default=0, nullable=False)
    last_accessed = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="memories")
    embedding = relationship("Embedding", back_populates="memory", uselist=False)
    
    def update_access(self) -> None:
        """Update access tracking when memory is retrieved."""
        self.access_count += 1
        self.last_accessed = datetime.utcnow()
    
    def __repr__(self) -> str:
        return f"<UserMemory(id={self.id}, user_id={self.user_id}, type='{self.memory_type}')>"


class Embedding(Base):
    """Vector embeddings for semantic search and memory retrieval."""
    
    __tablename__ = "embedding"
    
    id = Column(Integer, primary_key=True, index=True)
    memory_id = Column(Integer, ForeignKey("usermemory.id"), unique=True, nullable=False)
    
    # Embedding data
    vector = Column(LargeBinary, nullable=False)  # serialized numpy array or similar
    dimensions = Column(Integer, nullable=False)  # embedding vector dimensions
    model_name = Column(String(100), nullable=False)  # which embedding model was used
    
    # Metadata
    is_valid = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    memory = relationship("UserMemory", back_populates="embedding")
    
    def __repr__(self) -> str:
        return f"<Embedding(id={self.id}, memory_id={self.memory_id}, dimensions={self.dimensions})>"


class Conversation(Base):
    """Conversation history for AI interactions."""
    
    __tablename__ = "conversation"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    
    # Conversation metadata
    session_id = Column(String(255), nullable=False)  # unique session identifier
    conversation_type = Column(String(50), default="general", nullable=False)  # general, career, finance, etc.
    
    # Message content
    messages = Column(JSON, nullable=False)  # array of message objects
    summary = Column(Text, nullable=True)  # AI-generated summary of the conversation
    
    # Context
    context_data = Column(JSON, nullable=True)  # relevant user data at time of conversation
    
    # Status and metadata
    is_active = Column(Boolean, default=True, nullable=False)
    message_count = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_message_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    
    def add_message(self, role: str, content: str, metadata: dict = None) -> None:
        """Add a new message to the conversation."""
        import json
        
        message = {
            "role": role,  # user, assistant, system
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        if isinstance(self.messages, str):
            current_messages = json.loads(self.messages)
        else:
            current_messages = self.messages or []
        
        current_messages.append(message)
        self.messages = json.dumps(current_messages)
        self.message_count = len(current_messages)
        self.last_message_at = datetime.utcnow()
    
    def end_conversation(self) -> None:
        """Mark conversation as ended."""
        self.is_active = False
        self.ended_at = datetime.utcnow()
    
    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, user_id={self.user_id}, messages={self.message_count})>"