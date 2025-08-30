from celery import shared_task
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.habits import Habit
from app.models.user import User
from app.services.ai_service import AIService
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_daily_habit_reminders():
    """Send daily habit reminders to users"""
    try:
        db = SessionLocal()
        ai_service = AIService()
        
        # Get all active habits
        active_habits = db.query(Habit).filter(Habit.is_active == True).all()
        
        for habit in active_habits:
            try:
                # Check if habit was completed today
                today = datetime.now().date()
                completed_today = db.query(Habit).filter(
                    Habit.id == habit.id,
                    Habit.completed_at >= today
                ).first()
                
                if not completed_today:
                    # Send reminder
                    user = db.query(User).filter(User.id == habit.user_id).first()
                    if user:
                        reminder_message = f"Don't forget to complete your habit: {habit.name}"
                        logger.info(f"Sending reminder to user {user.id} for habit {habit.id}")
                        
                        # TODO: Implement actual notification sending
                        # This could be email, push notification, etc.
                        
            except Exception as e:
                logger.error(f"Error processing habit {habit.id}: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"Error in daily habit reminders: {str(e)}")
    finally:
        db.close()

@shared_task
def send_habit_streak_alerts():
    """Send alerts for habit streaks"""
    try:
        db = SessionLocal()
        
        # Get habits with significant streaks
        high_streak_habits = db.query(Habit).filter(
            Habit.current_streak >= 7  # 1 week or more
        ).all()
        
        for habit in high_streak_habits:
            try:
                user = db.query(User).filter(User.id == habit.user_id).first()
                if user:
                    streak_message = f"Amazing! You've maintained {habit.name} for {habit.current_streak} days!"
                    logger.info(f"Sending streak alert to user {user.id} for habit {habit.id}")
                    
                    # TODO: Implement actual notification sending
                    
            except Exception as e:
                logger.error(f"Error processing streak alert for habit {habit.id}: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"Error in habit streak alerts: {str(e)}")
    finally:
        db.close()

@shared_task
def check_missed_habits():
    """Check for missed habits and send recovery messages"""
    try:
        db = SessionLocal()
        ai_service = AIService()
        
        # Get habits that haven't been completed in 2+ days
        two_days_ago = datetime.now() - timedelta(days=2)
        missed_habits = db.query(Habit).filter(
            Habit.is_active == True,
            Habit.completed_at < two_days_ago
        ).all()
        
        for habit in missed_habits:
            try:
                user = db.query(User).filter(User.id == habit.user_id).first()
                if user:
                    recovery_message = f"It's been a while since you completed '{habit.name}'. Don't give up - every day is a new opportunity!"
                    logger.info(f"Sending recovery message to user {user.id} for habit {habit.id}")
                    
                    # TODO: Implement actual notification sending
                    
            except Exception as e:
                logger.error(f"Error processing recovery message for habit {habit.id}: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"Error in missed habits check: {str(e)}")
    finally:
        db.close()
