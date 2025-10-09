"""Gamification models for badges, achievements, and user stats."""

from datetime import datetime, date, timedelta
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Date, ForeignKey, Integer, String, Text, Float, JSON
from sqlalchemy.orm import relationship

from ..db.session import Base


class Badge(Base):
    """Badge definitions for the gamification system."""
    
    __tablename__ = "badge"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    
    # Badge properties
    category = Column(String(100), nullable=False)  # habits, career, finance, mood, etc.
    badge_type = Column(String(50), default="achievement", nullable=False)  # achievement, milestone, streak
    difficulty = Column(String(20), default="easy", nullable=False)  # easy, medium, hard, legendary
    
    # Visual properties
    icon_url = Column(String(500), nullable=True)
    color = Column(String(7), nullable=True)  # hex color code
    
    # Requirements (JSON structure defining how to earn this badge)
    requirements = Column(JSON, nullable=False)
    
    # Metadata
    points_value = Column(Integer, default=10, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_secret = Column(Boolean, default=False, nullable=False)  # hidden until earned
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user_badges = relationship("UserBadge", back_populates="badge")
    
    def __repr__(self) -> str:
        return f"<Badge(id={self.id}, name='{self.name}', category='{self.category}')>"


class UserBadge(Base):
    """User's earned badges."""
    
    __tablename__ = "userbadge"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    badge_id = Column(Integer, ForeignKey("badge.id"), nullable=False)
    
    # Earning details
    earned_date = Column(Date, default=date.today, nullable=False)
    earned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Context of earning
    trigger_event = Column(String(255), nullable=True)  # what action triggered this badge
    progress_snapshot = Column(JSON, nullable=True)  # user's stats when badge was earned
    
    # Display preferences
    is_displayed = Column(Boolean, default=True, nullable=False)
    display_order = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="user_badges")
    badge = relationship("Badge", back_populates="user_badges")
    
    def __repr__(self) -> str:
        return f"<UserBadge(user_id={self.user_id}, badge_id={self.badge_id}, earned={self.earned_date})>"


class Achievement(Base):
    """Achievement definitions and tracking."""
    
    __tablename__ = "achievement"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    
    # Achievement properties
    category = Column(String(100), nullable=False)
    achievement_type = Column(String(50), default="milestone", nullable=False)  # milestone, streak, challenge
    
    # Requirements and rewards
    target_value = Column(Float, nullable=False)  # target number to reach
    measurement_unit = Column(String(50), nullable=False)  # days, habits, points, etc.
    points_reward = Column(Integer, default=50, nullable=False)
    
    # Visual and metadata
    icon_url = Column(String(500), nullable=True)
    difficulty_level = Column(Integer, default=1, nullable=False)  # 1-5 scale
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_repeatable = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user_achievements = relationship("UserAchievement", back_populates="achievement")
    
    def __repr__(self) -> str:
        return f"<Achievement(id={self.id}, name='{self.name}', target={self.target_value})>"


class UserAchievement(Base):
    """User's achievement progress and completions."""
    
    __tablename__ = "userachievement"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    achievement_id = Column(Integer, ForeignKey("achievement.id"), nullable=False)
    
    # Progress tracking
    current_value = Column(Float, default=0.0, nullable=False)
    progress_percentage = Column(Float, default=0.0, nullable=False)
    
    # Completion
    is_completed = Column(Boolean, default=False, nullable=False)
    completed_date = Column(Date, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_progress_update = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="user_achievements")
    achievement = relationship("Achievement", back_populates="user_achievements")
    
    def update_progress(self, new_value: float) -> None:
        """Update achievement progress."""
        self.current_value = new_value
        self.progress_percentage = min((new_value / self.achievement.target_value) * 100, 100)
        self.last_progress_update = datetime.utcnow()
        
        if self.progress_percentage >= 100 and not self.is_completed:
            self.is_completed = True
            self.completed_date = date.today()
            self.completed_at = datetime.utcnow()
    
    def __repr__(self) -> str:
        return f"<UserAchievement(user_id={self.user_id}, achievement_id={self.achievement_id}, progress={self.progress_percentage}%)>"


class UserStats(Base):
    """User statistics for gamification and analytics."""
    
    __tablename__ = "userstats"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), unique=True, nullable=False)
    
    # Points and level
    total_points = Column(Integer, default=0, nullable=False)
    current_level = Column(Integer, default=1, nullable=False)
    points_to_next_level = Column(Integer, default=100, nullable=False)
    
    # Streak tracking
    current_login_streak = Column(Integer, default=0, nullable=False)
    longest_login_streak = Column(Integer, default=0, nullable=False)
    current_habit_streak = Column(Integer, default=0, nullable=False)
    longest_habit_streak = Column(Integer, default=0, nullable=False)
    
    # Activity metrics
    total_habits_completed = Column(Integer, default=0, nullable=False)
    total_tasks_completed = Column(Integer, default=0, nullable=False)
    total_mood_logs = Column(Integer, default=0, nullable=False)
    total_expenses_logged = Column(Integer, default=0, nullable=False)
    
    # Achievement counts
    badges_earned = Column(Integer, default=0, nullable=False)
    achievements_completed = Column(Integer, default=0, nullable=False)
    
    # Time-based stats
    days_active = Column(Integer, default=0, nullable=False)
    last_activity_date = Column(Date, nullable=True)
    
    # Weekly/Monthly aggregates
    weekly_points = Column(Integer, default=0, nullable=False)
    monthly_points = Column(Integer, default=0, nullable=False)
    weekly_reset_date = Column(Date, nullable=True)
    monthly_reset_date = Column(Date, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="stats")
    
    def add_points(self, points: int) -> None:
        """Add points and handle level progression."""
        self.total_points += points
        self.weekly_points += points
        self.monthly_points += points
        
        # Check for level up
        while self.total_points >= self.points_to_next_level:
            self.current_level += 1
            # Simple progression: each level requires 100 more points than the previous
            self.points_to_next_level = self.current_level * 100
    
    def update_activity(self) -> None:
        """Update activity-related stats."""
        today = date.today()
        if self.last_activity_date != today:
            self.days_active += 1
            # Update login streak
            if self.last_activity_date == today - timedelta(days=1):
                self.current_login_streak += 1
            else:
                self.current_login_streak = 1
            
            if self.current_login_streak > self.longest_login_streak:
                self.longest_login_streak = self.current_login_streak
            
            self.last_activity_date = today
    
    def __repr__(self) -> str:
        return f"<UserStats(user_id={self.user_id}, level={self.current_level}, points={self.total_points})>"