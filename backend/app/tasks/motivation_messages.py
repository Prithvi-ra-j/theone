from celery import shared_task
from app.services.ai_service import AIService
from app.db.session import SessionLocal
from app.models.user import User
from app.models.mood import MoodLog
from sqlalchemy import func
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_daily_motivation():
    """Send daily motivational messages to users"""
    try:
        db = SessionLocal()
        ai_service = AIService()
        
        # Get all users
        users = db.query(User).all()
        
        for user in users:
            try:
                # Get user's recent mood data
                week_ago = datetime.now() - timedelta(days=7)
                recent_moods = db.query(MoodLog).filter(
                    MoodLog.user_id == user.id,
                    MoodLog.logged_at >= week_ago
                ).all()
                
                # Calculate average mood
                if recent_moods:
                    avg_mood = sum(mood.mood_score for mood in recent_moods) / len(recent_moods)
                    
                    # Generate personalized motivation based on mood
                    if avg_mood < 5:
                        motivation_type = "encouragement"
                    elif avg_mood < 7:
                        motivation_type = "support"
                    else:
                        motivation_type = "celebration"
                    
                    # Get AI-generated motivation
                    user_context = {
                        "name": user.name,
                        "avg_mood": avg_mood,
                        "motivation_type": motivation_type
                    }
                    
                    motivation = await ai_service.motivation_nudge(user_context)
                    logger.info(f"Sending daily motivation to user {user.id}")
                    
                    # TODO: Implement actual notification sending
                    
            except Exception as e:
                logger.error(f"Error processing motivation for user {user.id}: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"Error in daily motivation: {str(e)}")
    finally:
        db.close()

@shared_task
def send_achievement_celebrations():
    """Send celebration messages for achievements"""
    try:
        db = SessionLocal()
        
        # Get recent achievements (last 24 hours)
        day_ago = datetime.now() - timedelta(days=1)
        recent_achievements = db.query(Achievement).filter(
            Achievement.achieved_at >= day_ago
        ).all()
        
        for achievement in recent_achievements:
            try:
                user = db.query(User).filter(User.id == achievement.user_id).first()
                if user:
                    celebration_message = f"🎉 Congratulations {user.name}! You've earned: {achievement.title}"
                    logger.info(f"Sending achievement celebration to user {user.id}")
                    
                    # TODO: Implement actual notification sending
                    
            except Exception as e:
                logger.error(f"Error processing achievement celebration for {achievement.id}: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"Error in achievement celebrations: {str(e)}")
    finally:
        db.close()
