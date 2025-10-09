"""Mood tracking models for mental wellness monitoring."""

from datetime import datetime, date, time
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Date, Time, ForeignKey, Integer, String, Text, Float, JSON
from sqlalchemy.orm import relationship

from ..db.session import Base


class MoodLog(Base):
    """Mood tracking and mental wellness model."""
    
    __tablename__ = "moodlog"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    
    # Mood metrics
    mood_score = Column(Integer, nullable=False)  # 1-10 scale (1=very bad, 10=excellent)
    energy_level = Column(Integer, nullable=True)  # 1-10 scale
    stress_level = Column(Integer, nullable=True)  # 1-10 scale
    anxiety_level = Column(Integer, nullable=True)  # 1-10 scale
    
    # Mood descriptors
    primary_emotion = Column(String(50), nullable=True)  # happy, sad, anxious, excited, etc.
    secondary_emotions = Column(String(255), nullable=True)  # comma-separated list
    
    # Context and triggers
    activities = Column(JSON, nullable=True)  # JSON array of activities done today
    triggers = Column(JSON, nullable=True)  # JSON array of potential mood triggers
    location = Column(String(100), nullable=True)
    weather = Column(String(50), nullable=True)
    
    # Physical factors
    sleep_hours = Column(Float, nullable=True)
    sleep_quality = Column(Integer, nullable=True)  # 1-10 scale
    exercise_minutes = Column(Integer, nullable=True)
    social_interactions = Column(Integer, nullable=True)  # number of meaningful interactions
    
    # Additional context
    notes = Column(Text, nullable=True)
    gratitude_notes = Column(Text, nullable=True)  # what they're grateful for
    
    # Timing
    log_date = Column(Date, default=date.today, nullable=False)
    log_time = Column(Time, nullable=True)
    logged_at = Column(DateTime, nullable=False)
    
    # Metadata
    entry_method = Column(String(20), default="manual", nullable=False)  # manual, reminder, check_in
    is_private = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="mood_logs")
    
    def get_mood_category(self) -> str:
        """Get mood category based on mood score."""
        if self.mood_score <= 3:
            return "poor"
        elif self.mood_score <= 5:
            return "below_average"
        elif self.mood_score <= 7:
            return "average"
        elif self.mood_score <= 8:
            return "good"
        else:
            return "excellent"
    
    def __repr__(self) -> str:
        return f"<MoodLog(id={self.id}, user_id={self.user_id}, mood_score={self.mood_score}, date={self.log_date})>"