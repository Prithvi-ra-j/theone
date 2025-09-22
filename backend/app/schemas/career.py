"""Career-related schemas for API requests and responses."""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class CareerGoalBase(BaseModel):
    """Base career goal schema."""
    title: str = Field(..., min_length=1, max_length=255, description="Goal title")
    description: Optional[str] = Field(None, max_length=2000, description="Goal description")
    target_date: Optional[datetime] = Field(None, description="Target completion date")
    priority: str = Field(default="medium", description="Goal priority (low, medium, high)")
    status: str = Field(default="active", description="Goal status")


class CareerGoalCreate(CareerGoalBase):
    """Schema for creating a career goal."""
    pass


class CareerGoalUpdate(BaseModel):
    """Schema for updating a career goal."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    target_date: Optional[datetime] = None
    priority: Optional[str] = Field(None, description="Goal priority (low, medium, high)")
    status: Optional[str] = Field(None, description="Goal status")
    progress: Optional[float] = Field(None, ge=0.0, le=100.0, description="Progress percentage")


class CareerGoalRead(CareerGoalBase):
    """Schema for reading a career goal."""
    id: int
    user_id: int
    progress: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SkillBase(BaseModel):
    """Base skill schema."""
    name: str = Field(..., min_length=1, max_length=255, description="Skill name")
    description: Optional[str] = Field(None, max_length=1000, description="Skill description")
    category: Optional[str] = Field(None, max_length=100, description="Skill category")
    current_level: int = Field(default=1, ge=1, le=10, description="Current skill level (1-10)")
    target_level: int = Field(default=5, ge=1, le=10, description="Target skill level (1-10)")
    is_core_skill: bool = Field(default=False, description="Whether this is a core skill")


class SkillCreate(SkillBase):
    """Schema for creating a skill."""
    career_goal_id: Optional[int] = Field(None, description="Associated career goal ID")


class SkillUpdate(BaseModel):
    """Schema for updating a skill."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, max_length=100)
    current_level: Optional[int] = Field(None, ge=1, le=10)
    target_level: Optional[int] = Field(None, ge=1, le=10)
    is_core_skill: Optional[bool] = None
    career_goal_id: Optional[int] = None


class SkillRead(SkillBase):
    """Schema for reading a skill."""
    id: int
    user_id: int
    career_goal_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LearningPathBase(BaseModel):
    """Base learning path schema."""
    title: str = Field(..., min_length=1, max_length=255, description="Learning path title")
    description: Optional[str] = Field(None, max_length=2000, description="Learning path description")
    estimated_hours: Optional[int] = Field(None, ge=1, description="Estimated hours to complete")
    difficulty: str = Field(default="beginner", description="Difficulty level")
    status: str = Field(default="planned", description="Learning path status")


class LearningPathCreate(LearningPathBase):
    """Schema for creating a learning path."""
    skill_id: int = Field(..., description="Associated skill ID")


class LearningPathUpdate(BaseModel):
    """Schema for updating a learning path."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    estimated_hours: Optional[int] = Field(None, ge=1)
    difficulty: Optional[str] = Field(None, description="Difficulty level")
    status: Optional[str] = Field(None, description="Learning path status")
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class LearningPathRead(LearningPathBase):
    """Schema for reading a learning path."""
    id: int
    user_id: int
    skill_id: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CareerDashboard(BaseModel):
    """Schema for career dashboard data."""
    user_id: int
    total_goals: int
    active_goals: int
    completed_goals: int
    total_skills: int
    skills_in_progress: int
    average_skill_level: float
    recent_goals: List[CareerGoalRead]
    top_skills: List[SkillRead]
    learning_paths: List[LearningPathRead]
    
    class Config:
        from_attributes = True


class SkillRecommendation(BaseModel):
    """Schema for AI-generated skill recommendations."""
    skill_name: str
    description: str
    category: str
    reason: str
    priority: str
    estimated_effort: str
    related_skills: List[str]
    learning_resources: List[str]


class RoadmapTask(BaseModel):
    title: str
    description: Optional[str] = None
    est_hours: Optional[int] = None

    class Config:
        schema_extra = {
            "example": {
                "title": "Read ""Introduction to Algorithms""",
                "description": "Skim chapters 1-3",
                "est_hours": 6
            }
        }


class RoadmapMilestone(BaseModel):
    title: str
    description: Optional[str] = None
    estimated_weeks: Optional[int] = None
    tasks: List[RoadmapTask] = []

    class Config:
        schema_extra = {
            "example": {
                "title": "Foundations",
                "description": "Build core CS fundamentals",
                "estimated_weeks": 4,
                "tasks": [
                    {"title": "Read intro", "description": "Chapters 1-3", "est_hours": 6}
                ]
            }
        }

