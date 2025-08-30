"""User schemas for API requests and responses."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""
    name: str = Field(..., min_length=1, max_length=255, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")


class UserCreate(UserBase):
    """Schema for user creation."""
    password: str = Field(..., min_length=8, description="User's password (min 8 characters)")
    bio: Optional[str] = Field(None, max_length=1000, description="User's bio")
    phone_number: Optional[str] = Field(None, max_length=20, description="User's phone number")


class UserUpdate(BaseModel):
    """Schema for user updates."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    bio: Optional[str] = Field(None, max_length=1000)
    avatar_url: Optional[str] = Field(None, max_length=500)
    phone_number: Optional[str] = Field(None, max_length=20)
    preferences: Optional[dict] = Field(None, description="User preferences as JSON")


class UserRead(UserBase):
    """Schema for user reading."""
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]
    avatar_url: Optional[str]
    bio: Optional[str]
    phone_number: Optional[str]
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class Token(BaseModel):
    """Schema for authentication token."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class TokenData(BaseModel):
    """Schema for token data."""
    email: Optional[str] = None
    user_id: Optional[int] = None


class UserPreferences(BaseModel):
    """Schema for user preferences."""
    daily_tips_enabled: bool = Field(default=True, description="Enable daily tips")
    notification_style: str = Field(default="gentle", description="Notification style (gentle, assertive, minimal)")
    hybrid_roadmap_choice: str = Field(default="both", description="Roadmap focus (career, life, both)")
    theme: str = Field(default="light", description="UI theme preference")
    language: str = Field(default="en", description="Preferred language")
    timezone: str = Field(default="Asia/Kolkata", description="User's timezone")
    
    # Career preferences
    career_focus_areas: list[str] = Field(default_factory=list, description="Areas of career interest")
    skill_development_goals: list[str] = Field(default_factory=list, description="Skills to develop")
    
    # Life preferences
    wellness_goals: list[str] = Field(default_factory=list, description="Wellness and life goals")
    habit_reminders: bool = Field(default=True, description="Enable habit reminders")
    
    # Financial preferences
    financial_goals: list[str] = Field(default_factory=list, description="Financial goals")
    budget_alerts: bool = Field(default=True, description="Enable budget alerts")


class UserProfile(UserRead):
    """Extended user profile with preferences."""
    preferences: Optional[UserPreferences] = None
    
    class Config:
        from_attributes = True


class PasswordChange(BaseModel):
    """Schema for password change."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password (min 8 characters)")


class PasswordReset(BaseModel):
    """Schema for password reset request."""
    email: EmailStr = Field(..., description="User's email address")


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password (min 8 characters)")
