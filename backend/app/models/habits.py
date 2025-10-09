"""Habit tracking models for building positive routines."""

from datetime import datetime, date, time
from typing import Optional, List

from sqlalchemy import Boolean, Column, DateTime, Date, Time, ForeignKey, Integer, String, Text, Float
from sqlalchemy.orm import relationship

from ..db.session import Base


class Habit(Base):
    """Habit definition and tracking model."""
    
    __tablename__ = "habit"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False)  # e.g., 'health', 'productivity', 'learning', 'wellness'
    
    # Habit configuration
    frequency = Column(String(20), default="daily", nullable=False)  # daily, weekly, custom
    target_value = Column(Float, nullable=True)  # e.g., 30 minutes, 5 pages, 10 pushups
    unit = Column(String(50), nullable=True)  # e.g., 'minutes', 'pages', 'reps', 'glasses'
    
    # Scheduling
    preferred_time = Column(Time, nullable=True)  # preferred time of day
    reminder_enabled = Column(Boolean, default=True, nullable=False)
    reminder_time = Column(Time, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    difficulty_level = Column(String(20), default="easy", nullable=False)  # easy, medium, hard
    
    # Tracking
    current_streak = Column(Integer, default=0, nullable=False)
    longest_streak = Column(Integer, default=0, nullable=False)
    total_completions = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_completed = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="habits")
    completions = relationship("HabitCompletion", back_populates="habit", cascade="all, delete-orphan")
    
    def mark_completed(self, completion_date: Optional[date] = None) -> None:
        """Mark habit as completed for the given date."""
        if completion_date is None:
            completion_date = date.today()
        
        self.last_completed = datetime.utcnow()
        self.total_completions += 1
        
        # Update streak logic would go here
        # For now, just increment current streak
        self.current_streak += 1
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak
    
    def __repr__(self) -> str:
        return f"<Habit(id={self.id}, name='{self.name}', category='{self.category}')>"


class Task(Base):
    """Task model for tracking to-do items."""
    
    __tablename__ = "task"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Task details
    priority = Column(String(20), default="medium", nullable=False)  # low, medium, high
    status = Column(String(20), default="pending", nullable=False)  # pending, in_progress, completed, cancelled
    
    # Dates
    due_date = Column(Date, nullable=True)
    due_time = Column(Time, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Reminders
    reminder_enabled = Column(Boolean, default=False, nullable=False)
    reminder_time = Column(DateTime, nullable=True)
    
    # Metadata
    category = Column(String(100), nullable=True)  # work, personal, etc.
    tags = Column(String(255), nullable=True)  # comma-separated tags

    # Estimated time to complete (in minutes)
    estimated_minutes = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="tasks")
    
    def mark_completed(self) -> None:
        """Mark task as completed."""
        self.status = "completed"
        self.completed_at = datetime.utcnow()
    
    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title='{self.title}', status='{self.status}')>"


class CalendarEvent(Base):
    """Calendar event model for scheduling and tracking events."""
    
    __tablename__ = "calendarevent"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Event timing
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)
    all_day = Column(Boolean, default=False, nullable=False)

    # Start time (for compatibility with API expectations)
    start_time = Column(Time, nullable=True)
    
    # Recurrence
    is_recurring = Column(Boolean, default=False, nullable=False)
    recurrence_pattern = Column(String(100), nullable=True)  # daily, weekly, monthly, custom
    recurrence_end_date = Column(Date, nullable=True)
    
    # Location
    location = Column(String(255), nullable=True)
    is_virtual = Column(Boolean, default=False, nullable=False)
    meeting_link = Column(String(255), nullable=True)
    
    # Reminders
    reminder_enabled = Column(Boolean, default=True, nullable=False)
    reminder_time = Column(Integer, default=15, nullable=True)  # minutes before event
    
    # Status
    status = Column(String(20), default="confirmed", nullable=False)  # confirmed, tentative, cancelled
    
    # Metadata
    category = Column(String(100), nullable=True)  # work, personal, etc.
    color = Column(String(20), nullable=True)  # for UI display
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="calendar_events")
    
    def __repr__(self) -> str:
        return f"<CalendarEvent(id={self.id}, title='{self.title}', start='{self.start_datetime}')>"


class HabitCompletion(Base):
    """Individual habit completion records."""
    
    __tablename__ = "habitcompletion"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    habit_id = Column(Integer, ForeignKey("habit.id"), nullable=False)
    
    # Completion details
    completed_date = Column(Date, default=date.today, nullable=False)
    completed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    actual_value = Column(Float, nullable=True)  # actual value achieved (e.g., 45 minutes instead of 30)
    
    # Quality and notes
    quality_rating = Column(Integer, nullable=True)  # 1-5 rating of how well they did
    notes = Column(Text, nullable=True)
    mood_before = Column(Integer, nullable=True)  # 1-10 scale
    mood_after = Column(Integer, nullable=True)  # 1-10 scale
    
    # Context
    location = Column(String(100), nullable=True)
    weather = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="habit_completions")
    habit = relationship("Habit", back_populates="completions")
    
    def __repr__(self) -> str:
        return f"<HabitCompletion(id={self.id}, habit_id={self.habit_id}, date={self.completed_date})>"


class HabitLog(Base):
    """Extended habit logging for detailed tracking and analysis."""
    
    __tablename__ = "habitlog"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    habit_id = Column(Integer, ForeignKey("habit.id"), nullable=False)
    
    # Log details
    date = Column(Date, default=date.today, nullable=False)
    completed = Column(Boolean, default=False, nullable=False)
    value = Column(Float, nullable=True)  # actual value logged
    
    # Additional context
    notes = Column(Text, nullable=True)
    difficulty_rating = Column(Integer, nullable=True)  # 1-5 scale
    satisfaction_rating = Column(Integer, nullable=True)  # 1-5 scale
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User")
    habit = relationship("Habit")
    
    def __repr__(self) -> str:
        return f"<HabitLog(id={self.id}, habit_id={self.habit_id}, date={self.date}, completed={self.completed})>"