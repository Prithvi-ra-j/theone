from celery import shared_task
from app.services.ai_service import AIService
from app.services.memory_service import MemoryService
from app.db.session import SessionLocal
from ..models.user import User
from ..models.mood import MoodLog
from ..models.habits import Habit, HabitCompletion
from ..models.finance import Expense
from sqlalchemy import func
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@shared_task
def generate_weekly_insights():
    """Generate weekly AI insights for users"""
    try:
        db = SessionLocal()
        ai_service = AIService()
        memory_service = MemoryService()
        
        # Get all users
        users = db.query(User).all()
        
        for user in users:
            try:
                # Collect user data for the week
                week_ago = datetime.now() - timedelta(days=7)
                
                # Mood data
                weekly_moods = db.query(MoodLog).filter(
                    MoodLog.user_id == user.id,
                    MoodLog.logged_at >= week_ago
                ).all()
                
                # Habit data
                weekly_habits = db.query(HabitCompletion).filter(
                    HabitCompletion.user_id == user.id,
                    HabitCompletion.completed_at >= week_ago
                ).all()
                
                # Finance data
                weekly_expenses = db.query(func.sum(Expense.amount)).filter(
                    Expense.user_id == user.id,
                    Expense.date >= week_ago
                ).scalar() or 0
                
                # Generate insights
                user_context = {
                    "name": user.name,
                    "weekly_mood_data": [mood.mood_score for mood in weekly_moods],
                    "weekly_habits_completed": len(weekly_habits),
                    "weekly_expenses": weekly_expenses,
                    "insight_type": "weekly_summary"
                }
                
                insights = ai_service.personalized_insight(user_context)  # type: ignore
                logger.info(f"Generated weekly insights for user {user.id}")
                
                # Store insights in memory
                memory_service.store_memory(
                    user_id=user.id,
                    content=str(insights),
                    memory_type="weekly_insights",
                    metadata={"generated_at": datetime.now().isoformat()}
                )
                
                # TODO: Send insights to user via notification
                
            except Exception as e:
                logger.error(f"Error generating insights for user {user.id}: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"Error in weekly insights generation: {str(e)}")
    finally:
        db.close()

@shared_task
def generate_personalized_recommendations():
    """Generate personalized recommendations based on user behavior"""
    try:
        db = SessionLocal()
        ai_service = AIService()
        memory_service = MemoryService()
        
        # Get users with sufficient data
        users = db.query(User).all()
        
        for user in users:
            try:
                # Get user's recent activity patterns
                month_ago = datetime.now() - timedelta(days=30)
                
                # Habit patterns
                habit_patterns = db.query(Habit).filter(
                    Habit.user_id == user.id,
                    Habit.created_at >= month_ago
                ).all()
                
                # Mood trends
                mood_trends = db.query(MoodLog).filter(
                    MoodLog.user_id == user.id,
                    MoodLog.logged_at >= month_ago
                ).order_by(MoodLog.logged_at.desc()).limit(10).all()
                
                # Generate recommendations
                user_context = {
                    "name": user.name,
                    "habit_patterns": [habit.name for habit in habit_patterns],
                    "mood_trends": [mood.mood_score for mood in mood_trends],
                    "recommendation_type": "behavior_analysis"
                }
                
                recommendations = ai_service.personalized_insight(user_context)  # type: ignore
                logger.info(f"Generated personalized recommendations for user {user.id}")
                
                # Store recommendations
                memory_service.store_memory(
                    user_id=user.id,
                    content=str(recommendations),
                    memory_type="recommendations",
                    metadata={"generated_at": datetime.now().isoformat()}
                )
                
                # TODO: Send recommendations to user
                
            except Exception as e:
                logger.error(f"Error generating recommendations for user {user.id}: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"Error in personalized recommendations: {str(e)}")
    finally:
        db.close()

@shared_task
def analyze_user_patterns():
    """Analyze user patterns for long-term insights"""
    try:
        db = SessionLocal()
        ai_service = AIService()
        memory_service = MemoryService()
        
        # Get users with 3+ months of data
        three_months_ago = datetime.now() - timedelta(days=90)
        users = db.query(User).filter(User.created_at <= three_months_ago).all()
        
        for user in users:
            try:
                # Long-term pattern analysis
                long_term_moods = db.query(MoodLog).filter(
                    MoodLog.user_id == user.id,
                    MoodLog.logged_at >= three_months_ago
                ).all()
                
                long_term_habits = db.query(Habit).filter(
                    Habit.user_id == user.id,
                    Habit.created_at >= three_months_ago
                ).all()
                
                # Generate long-term insights
                user_context = {
                    "name": user.name,
                    "long_term_mood_data": [mood.mood_score for mood in long_term_moods],
                    "long_term_habit_data": [habit.name for habit in long_term_habits],
                    "insight_type": "long_term_analysis"
                }
                
                long_term_insights = ai_service.personalized_insight(user_context)  # type: ignore
                logger.info(f"Generated long-term insights for user {user.id}")
                
                # Store long-term insights
                memory_service.store_memory(
                    user_id=user.id,
                    content=str(long_term_insights),
                    memory_type="long_term_insights",
                    metadata={"generated_at": datetime.now().isoformat()}
                )
                
            except Exception as e:
                logger.error(f"Error analyzing patterns for user {user.id}: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"Error in user pattern analysis: {str(e)}")
    finally:
        db.close()
