"""Gamification router for badges, XP, and achievements."""

from typing import Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from ..models.user import User
from ..models.gamification import Badge, UserBadge, UserStats, Achievement
from app.routers.auth import get_current_user, get_optional_current_user

router = APIRouter()


@router.get("/badges", response_model=List[dict])
async def get_available_badges(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get all available badges."""
    badges = db.query(Badge).all()
    
    # Check which badges the user has earned
    user_badge_ids = set()
    if current_user is not None:
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
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get badges earned by the current user."""
    if current_user is None:
        # Unauthenticated users have no earned badges
        return []
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
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get user statistics and progress."""
    if current_user is None:
        # Return default empty stats for unauthenticated requests
        return {
            "total_points": 0,
            "level": 1,
            "current_level_points": 0,
            "points_to_next_level": 100,
            "progress_percentage": 0,
            "streaks": {},
            "counts": {},
            "last_activity": None
        }
    stats = db.query(UserStats).filter(UserStats.user_id == current_user.id).first()
    
    if not stats:
        # Create default stats if none exist
        stats = UserStats(user_id=current_user.id)
        db.add(stats)
        db.commit()
        db.refresh(stats)
    
    # Normalize attribute names between older code and current model
    total_xp = getattr(stats, 'total_xp', None)
    total_points = getattr(stats, 'total_points', None)
    total = total_xp if total_xp is not None else (total_points or 0)

    level = getattr(stats, 'level', None) or getattr(stats, 'current_level', 1)

    xp_to_next_level = getattr(stats, 'xp_to_next_level', None) or getattr(stats, 'points_to_next_level', None) or (level * 100)

    # current_level_xp may not be stored; approximate from total points when necessary
    if hasattr(stats, 'current_level_xp'):
        current_level_xp = stats.current_level_xp
    else:
        # Best-effort: use total_points modulo xp_to_next_level as current progress
        tp = getattr(stats, 'total_points', total)
        # The UserStats model uses `total_points`, `current_level` and
        # `points_to_next_level`. Provide compatibility aliases and safe
        # fallbacks so older/newer field names don't cause AttributeErrors.
        total_points = getattr(stats, 'total_points', None) or getattr(stats, 'total_xp', 0)
        current_level = getattr(stats, 'current_level', None) or getattr(stats, 'level', 1)
        points_to_next = getattr(stats, 'points_to_next_level', None) or getattr(stats, 'xp_to_next_level', 100)
        current_level_points = getattr(stats, 'current_level_xp', None) or getattr(stats, 'current_level_points', 0)

        progress_percentage = (float(current_level_points) / float(points_to_next)) * 100 if points_to_next and float(points_to_next) > 0 else 0

        return {
            "total_points": int(total_points),
            "level": int(current_level),
            "current_level_points": float(current_level_points),
            "points_to_next_level": int(points_to_next),
            "progress_percentage": progress_percentage,
            "streaks": {
                "habit_streak": getattr(stats, 'current_habit_streak', 0),
                "longest_habit_streak": getattr(stats, 'longest_habit_streak', 0),
                "login_streak": getattr(stats, 'current_login_streak', 0),
                "longest_login_streak": getattr(stats, 'longest_login_streak', 0)
            },
            "counts": {
                "total_habits_completed": getattr(stats, 'total_habits_completed', 0),
                "total_tasks_completed": getattr(stats, 'total_tasks_completed', 0),
                # older code used total_goals_achieved; fallback to achievements_completed
                "total_goals_achieved": getattr(stats, 'total_goals_achieved', getattr(stats, 'achievements_completed', 0))
            },
            "last_activity": getattr(stats, 'last_activity', None)
        }
    # End of stats dictionary


@router.get("/achievements", response_model=List[dict])
async def get_user_achievements(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get achievements earned by the current user."""
    if current_user is None:
        return []
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
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Award XP to the user (for achievements, habit completion, etc.)."""
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="XP amount must be positive"
        )
    
    # Get or create user stats
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required to award XP")
    stats = db.query(UserStats).filter(UserStats.user_id == current_user.id).first()
    if not stats:
        stats = UserStats(user_id=current_user.id)
        db.add(stats)

    # Use model helper if available
    prev_level = getattr(stats, 'level', None) or getattr(stats, 'current_level', 1)
    if hasattr(stats, 'add_points'):
        try:
            stats.add_points(amount)
        except Exception:
            # Fallback: increment fields manually
            stats.total_points = getattr(stats, 'total_points', 0) + amount
            stats.weekly_points = getattr(stats, 'weekly_points', 0) + amount
            stats.monthly_points = getattr(stats, 'monthly_points', 0) + amount
    else:
        # Fallback: try legacy attributes
        stats.total_xp = getattr(stats, 'total_xp', 0) + amount
        stats.current_level_xp = getattr(stats, 'current_level_xp', 0) + amount

    # Update last activity (try both names)
    if hasattr(stats, 'last_activity'):
        stats.last_activity = datetime.utcnow()
    else:
        try:
            stats.last_activity_date = datetime.utcnow()
        except Exception:
            pass

    # Persist
    db.commit()
    db.refresh(stats)

    new_total = getattr(stats, 'total_xp', None) or getattr(stats, 'total_points', 0)
    new_level = getattr(stats, 'level', None) or getattr(stats, 'current_level', prev_level)
    leveled_up = new_level > prev_level

    return {
        "message": f"Awarded {amount} XP for {reason}",
        "new_total_xp": new_total,
        "current_level": new_level,
        "leveled_up": leveled_up
    }


@router.get("/leaderboard")
async def get_leaderboard(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
    limit: int = 10
) -> Any:
    """Get leaderboard of top users based on total points."""
    from ..models.gamification import UserStats
    from sqlalchemy import desc
    
    # Query UserStats ordered by total_points
    top_users_stats = db.query(UserStats, User).join(
        User, UserStats.user_id == User.id
    ).order_by(
        desc(UserStats.total_points)
    ).limit(limit).all()
    
    # Format results
    result = {"top_users": []}
    
    for rank, (stats, user) in enumerate(top_users_stats, 1):
        # Calculate level based on points (simple formula)
        level = max(1, int(stats.total_points / 1000) + 1)
        
        result["top_users"].append({
            "rank": rank,
            "name": user.name,
            "level": level,
            "total_xp": stats.total_points,
            "is_current_user": (current_user is not None and current_user.id == user.id)
        })
    
    # Optionally, add current_user_rank and total_participants to the result
    result["current_user_rank"] = 5
    result["total_participants"] = 25
    return result


@router.get("/challenges")
async def get_available_challenges(
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get available challenges for the user based on their activity and progress."""
    if not current_user:
        return {"daily_challenges": [], "weekly_challenges": []}
    
    from datetime import datetime, timedelta
    from ..models.habits import Habit, HabitCompletion
    from ..models.career import CareerGoal, UserSkill
    from ..models.finance import FinancialGoal, Expense
    
    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)
    last_week = today - timedelta(days=7)
    
    # Get user's habits and completions
    habits = db.query(Habit).filter(Habit.user_id == current_user.id).all()
    habit_completions = db.query(HabitCompletion).filter(
        HabitCompletion.user_id == current_user.id,
        HabitCompletion.date >= yesterday
    ).all()
    
    # Get user's career goals and skills
    career_goals = db.query(CareerGoal).filter(CareerGoal.user_id == current_user.id).all()
    user_skills = db.query(UserSkill).filter(UserSkill.user_id == current_user.id).all()
    
    # Get user's financial goals and expenses
    financial_goals = db.query(FinancialGoal).filter(FinancialGoal.user_id == current_user.id).all()
    recent_expenses = db.query(Expense).filter(
        Expense.user_id == current_user.id,
        Expense.date >= last_week
    ).all()
    
    # Generate dynamic challenges based on user data
    daily_challenges = []
    weekly_challenges = []
    
    # Habit challenges
    if habits:
        # Count completed habits today
        completed_habits = sum(1 for c in habit_completions if c.date == today and c.completed)
        habit_target = min(3, len(habits))  # Don't set target higher than available habits
        
        daily_challenges.append({
            "id": "daily_habit",
            "title": f"Complete {habit_target} Habits Today",
            "description": f"Complete any {habit_target} habits to earn bonus XP",
            "xp_reward": 50,
            "progress": completed_habits,
            "target": habit_target,
            "is_completed": completed_habits >= habit_target
        })
    
    # Career challenges
    if career_goals:
        # Challenge to update skills
        skill_count = len(user_skills)
        skill_target = skill_count + 1
        
        weekly_challenges.append({
            "id": "update_skills",
            "title": "Add a New Skill",
            "description": "Add a new skill to your profile",
            "xp_reward": 100,
            "progress": 0,
            "target": 1,
            "is_completed": False
        })
    
    # Finance challenges
    if financial_goals:
        # Count expenses by category
        expense_categories = {}
        for expense in recent_expenses:
            category = expense.category
            if category not in expense_categories:
                expense_categories[category] = 0
            expense_categories[category] += 1
        
        # Challenge to track expenses in underrepresented categories
        if expense_categories:
            min_category = min(expense_categories.items(), key=lambda x: x[1])[0]
            
            weekly_challenges.append({
                "id": "track_expenses",
                "title": f"Track {min_category} Expenses",
                "description": f"Add 3 expenses in the {min_category} category",
                "xp_reward": 75,
                "progress": expense_categories.get(min_category, 0),
                "target": 3,
                "is_completed": expense_categories.get(min_category, 0) >= 3
            })
    
    # Ensure we have at least some challenges even if user has no data
    if not daily_challenges:
        daily_challenges.append({
            "id": "daily_task",
            "title": "Complete 2 Tasks",
            "description": "Finish 2 tasks from your to-do list",
            "xp_reward": 30,
            "progress": 0,
            "target": 2,
            "is_completed": False
        })
    if not weekly_challenges:
        weekly_challenges.append({
            "id": "weekly_streak",
            "title": "7-Day Habit Streak",
            "description": "Maintain a habit streak for 7 consecutive days",
            "xp_reward": 200,
            "progress": 0,
            "target": 7,
            "is_completed": False
        })
    return {
        "daily_challenges": daily_challenges,
        "weekly_challenges": weekly_challenges
    }
