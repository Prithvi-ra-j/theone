"""Gamification router for badges, XP, and achievements."""

from typing import Any, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.gamification import Badge, UserBadge, UserStats, Achievement
from app.routers.auth import get_current_user

router = APIRouter()


@router.get("/badges", response_model=List[dict])
async def get_available_badges(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get all available badges."""
    badges = db.query(Badge).all()
    
    # Check which badges the user has earned
    user_badges = db.query(UserBadge.badge_id).filter(
        UserBadge.user_id == current_user.id
    ).all()
    user_badge_ids = {badge.badge_id for badge in user_badges}
    
    return [
        {
            "id": badge.id,
            "name": badge.name,
            "description": badge.description,
            "icon_url": badge.icon_url,
            "category": badge.category,
            "points": badge.points,
            "is_earned": badge.id in user_badge_ids,
            "earned_at": None  # Would be filled if earned
        }
        for badge in badges
    ]


@router.get("/my-badges", response_model=List[dict])
async def get_user_badges(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get badges earned by the current user."""
    user_badges = db.query(UserBadge, Badge).join(Badge).filter(
        UserBadge.user_id == current_user.id
    ).all()
    
    return [
        {
            "id": user_badge.id,
            "badge_name": badge.name,
            "badge_description": badge.description,
            "icon_url": badge.icon_url,
            "category": badge.category,
            "points": badge.points,
            "earned_at": user_badge.earned_at
        }
        for user_badge, badge in user_badges
    ]


@router.get("/stats", response_model=dict)
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get user statistics and progress."""
    stats = db.query(UserStats).filter(UserStats.user_id == current_user.id).first()
    
    if not stats:
        # Create default stats if none exist
        stats = UserStats(user_id=current_user.id)
        db.add(stats)
        db.commit()
        db.refresh(stats)
    
    return {
        "total_xp": stats.total_xp,
        "level": stats.level,
        "current_level_xp": stats.current_level_xp,
        "xp_to_next_level": stats.xp_to_next_level,
        "progress_percentage": (stats.current_level_xp / stats.xp_to_next_level) * 100 if stats.xp_to_next_level > 0 else 0,
        "streaks": {
            "habit_streak": stats.current_habit_streak,
            "longest_habit_streak": stats.longest_habit_streak,
            "login_streak": stats.current_login_streak,
            "longest_login_streak": stats.longest_login_streak
        },
        "counts": {
            "total_habits_completed": stats.total_habits_completed,
            "total_tasks_completed": stats.total_tasks_completed,
            "total_goals_achieved": stats.total_goals_achieved
        },
        "last_activity": stats.last_activity
    }


@router.get("/achievements", response_model=List[dict])
async def get_user_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get achievements earned by the current user."""
    achievements = db.query(Achievement).filter(
        Achievement.user_id == current_user.id
    ).order_by(Achievement.achieved_at.desc()).all()
    
    return [
        {
            "id": achievement.id,
            "type": achievement.type,
            "title": achievement.title,
            "description": achievement.description,
            "value": achievement.value,
            "xp_earned": achievement.xp_earned,
            "achieved_at": achievement.achieved_at
        }
        for achievement in achievements
    ]


@router.post("/award-xp")
async def award_xp(
    amount: int,
    reason: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Award XP to the user (for achievements, habit completion, etc.)."""
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="XP amount must be positive"
        )
    
    # Get or create user stats
    stats = db.query(UserStats).filter(UserStats.user_id == current_user.id).first()
    if not stats:
        stats = UserStats(user_id=current_user.id)
        db.add(stats)
    
    # Award XP
    stats.total_xp += amount
    stats.current_level_xp += amount
    stats.last_activity = datetime.utcnow()
    
    # Check for level up
    while stats.current_level_xp >= stats.xp_to_next_level:
        stats.current_level_xp -= stats.xp_to_next_level
        stats.level += 1
        stats.xp_to_next_level = stats.level * 100  # Simple level progression
    
    db.commit()
    
    return {
        "message": f"Awarded {amount} XP for {reason}",
        "new_total_xp": stats.total_xp,
        "current_level": stats.level,
        "leveled_up": stats.current_level_xp < amount  # Check if leveled up
    }


@router.get("/leaderboard")
async def get_leaderboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get leaderboard of top users."""
    # For MVP, return placeholder data
    # In production, this would query actual user stats
    
    return {
        "top_users": [
            {
                "rank": 1,
                "name": "Top Performer",
                "level": 15,
                "total_xp": 15000,
                "is_current_user": False
            },
            {
                "rank": 2,
                "name": "Consistent Learner",
                "level": 12,
                "total_xp": 12000,
                "is_current_user": False
            },
            {
                "rank": 3,
                "name": "Goal Setter",
                "level": 10,
                "total_xp": 10000,
                "is_current_user": False
            }
        ],
        "current_user_rank": 5,
        "total_participants": 25
    }


@router.get("/challenges")
async def get_available_challenges(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get available challenges for the user."""
    # For MVP, return placeholder challenges
    # In production, this would be dynamic based on user progress
    
    return {
        "daily_challenges": [
            {
                "id": "daily_habit",
                "title": "Complete 3 Habits Today",
                "description": "Complete any 3 habits to earn bonus XP",
                "xp_reward": 50,
                "progress": 0,
                "target": 3,
                "is_completed": False
            },
            {
                "id": "daily_task",
                "title": "Complete 2 Tasks",
                "description": "Finish 2 tasks from your to-do list",
                "xp_reward": 30,
                "progress": 0,
                "target": 2,
                "is_completed": False
            }
        ],
        "weekly_challenges": [
            {
                "id": "weekly_streak",
                "title": "7-Day Habit Streak",
                "description": "Maintain a habit streak for 7 consecutive days",
                "xp_reward": 200,
                "progress": 0,
                "target": 7,
                "is_completed": False
            }
        ]
    }
