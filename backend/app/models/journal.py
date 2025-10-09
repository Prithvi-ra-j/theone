"""Journaling models for Journal & Mood feature."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON, Float
from sqlalchemy.orm import relationship

from ..db.session import Base


class JournalEntry(Base):
    __tablename__ = "journal_entry"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    tags = Column(JSON, nullable=True)  # list of strings
    user_mood = Column(Integer, nullable=True)  # optional quick slider (-5..5 or 1..10)
    is_private = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    analysis = relationship("JournalAnalysis", back_populates="entry", uselist=False, cascade="all, delete-orphan")


class JournalAnalysis(Base):
    __tablename__ = "journal_analysis"

    id = Column(Integer, primary_key=True)
    journal_id = Column(Integer, ForeignKey("journal_entry.id"), nullable=False, index=True)

    mood_score = Column(Float, nullable=True)  # -5..5
    valence = Column(Float, nullable=True)
    arousal = Column(Float, nullable=True)
    emotions = Column(JSON, nullable=True)  # [{label, score}]
    topics = Column(JSON, nullable=True)  # list[str]
    triggers = Column(JSON, nullable=True)  # list[str]
    suggestions = Column(JSON, nullable=True)  # list[str]
    keywords = Column(JSON, nullable=True)  # list[str]
    summary = Column(Text, nullable=True)
    safety_flags = Column(JSON, nullable=True)  # list[str]

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    entry = relationship("JournalEntry", back_populates="analysis")
