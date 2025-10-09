"""Career models for goal tracking and skill development."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Float
from sqlalchemy.orm import relationship

from ..db.session import Base


class CareerGoal(Base):
    """Career goal tracking model."""
    
    __tablename__ = "careergoal"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    # Category is optional from the client; allow NULL at DB level to avoid insert errors
    # Also provide a server_default so inserts that omit the column will receive
    # a non-NULL default value at the DB level in case the schema still has
    # a NOT NULL constraint from an earlier migration state.
    category = Column(String(100), nullable=True, server_default="general")  # e.g., 'technical', 'leadership', 'certification'
    target_date = Column(DateTime, nullable=True)
    priority = Column(String(20), default="medium", nullable=False)  # low, medium, high, urgent
    status = Column(String(20), default="active", nullable=False)  # active, completed, paused, cancelled
    progress_percentage = Column(Float, default=0.0, nullable=False)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="career_goals")
    
    def __repr__(self) -> str:
        return f"<CareerGoal(id={self.id}, title='{self.title}', status='{self.status}')>"

    @property
    def progress(self) -> float:
        """Expose a `progress` attribute for Pydantic serialization (maps to progress_percentage)."""
        try:
            return float(self.progress_percentage or 0.0)
        except Exception:
            return 0.0


class Skill(Base):
    """Skill tracking and development model."""
    
    __tablename__ = "skill"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)  # e.g., 'technical', 'soft_skills', 'language'
    current_level = Column(String(20), default="beginner", nullable=False)  # beginner, intermediate, advanced, expert
    target_level = Column(String(20), default="intermediate", nullable=False)
    proficiency_score = Column(Float, default=0.0, nullable=False)  # 0-100
    is_priority = Column(Boolean, default=False, nullable=False)
    
    # Learning resources
    learning_resources = Column(Text, nullable=True)  # JSON string of resources
    practice_hours = Column(Float, default=0.0, nullable=False)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_practiced = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="skills")
    
    def __repr__(self) -> str:
        return f"<Skill(id={self.id}, name='{self.name}', level='{self.current_level}')>"


class LearningPath(Base):
    """Learning path and roadmap model."""
    
    __tablename__ = "learningpath"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    field = Column(String(100), nullable=False)  # e.g., 'data_science', 'web_development', 'ai_ml'
    difficulty_level = Column(String(20), default="beginner", nullable=False)
    estimated_duration_weeks = Column(Integer, nullable=True)
    
    # Progress tracking
    is_active = Column(Boolean, default=True, nullable=False)
    progress_percentage = Column(Float, default=0.0, nullable=False)
    current_milestone = Column(String(255), nullable=True)
    
    # Content (stored as JSON string)
    milestones = Column(Text, nullable=True)  # JSON array of milestones
    resources = Column(Text, nullable=True)  # JSON array of learning resources
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="learning_paths")
    
    def __repr__(self) -> str:
        return f"<LearningPath(id={self.id}, title='{self.title}', field='{self.field}')>"


class LearningPathMilestone(Base):
    """Milestones associated with a LearningPath."""

    __tablename__ = "learningpath_milestone"

    id = Column(Integer, primary_key=True, index=True)
    learning_path_id = Column(Integer, ForeignKey("learningpath.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=True)
    estimated_weeks = Column(Integer, nullable=True)
    status = Column(String(20), default="planned", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class LearningPathProject(Base):
    """Projects to gain practical experience within a LearningPath."""

    __tablename__ = "learningpath_project"

    id = Column(Integer, primary_key=True, index=True)
    learning_path_id = Column(Integer, ForeignKey("learningpath.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=True)
    est_hours = Column(Integer, nullable=True)
    status = Column(String(20), default="planned", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)