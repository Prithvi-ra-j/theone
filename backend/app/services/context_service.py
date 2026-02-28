"""Context service for aggregating site-wide user progress."""

from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.models.career import CareerGoal, Skill
from app.models.habits import Habit, HabitLog
from app.models.finance import Budget, Transaction
from app.models.mood import MoodLog

class ContextService:
    @staticmethod
    def get_user_progress_summary(db: Session, user_id: int) -> str:
        """Gather a summarized string of user's progress across the site."""
        summary = []
        
        # 1. Career Progress
        career_goals = db.query(CareerGoal).filter(CareerGoal.user_id == user_id, CareerGoal.status == "active").all()
        if career_goals:
            goal_titles = ", ".join([g.title for g in career_goals])
            summary.append(f"Active career goals: {goal_titles}.")
        
        # 2. Habit Streaks
        week_ago = datetime.utcnow() - timedelta(days=7)
        habits = db.query(Habit).filter(Habit.user_id == user_id, Habit.is_active == True).all()
        if habits:
            habit_names = ", ".join([h.name for h in habits])
            summary.append(f"Currently tracking {len(habits)} habits: {habit_names}.")
            
        # 3. Finance Status
        budgets = db.query(Budget).filter(Budget.user_id == user_id).all()
        if budgets:
            budget_summary = ", ".join([f"{b.category}: {b.limit_amount}" for b in budgets])
            summary.append(f"Active budgets: {budget_summary}.")
            
        # 4. Recent Mood
        recent_moods = db.query(MoodLog).filter(MoodLog.user_id == user_id).order_by(MoodLog.created_at.desc()).limit(3).all()
        if recent_moods:
            mood_scores = ", ".join([str(m.score) for m in recent_moods])
            summary.append(f"Latest mood scores (out of 10): {mood_scores}.")
            
        if not summary:
            return "User is just getting started and hasn't populated many features yet."
            
        return " ".join(summary)
