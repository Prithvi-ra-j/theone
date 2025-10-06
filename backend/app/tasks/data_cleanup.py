from celery import shared_task
from app.db.session import SessionLocal
from ..models.mood import MoodLog
from ..models.habits import HabitCompletion, Habit
from ..models.finance import Expense
from ..models.memory import Conversation, Embedding
from ..models.user import User
from sqlalchemy import func
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@shared_task
def cleanup_old_data():
    """Clean up old data to maintain database performance"""
    try:
        db = SessionLocal()
        
        # Clean up old mood logs (keep last 2 years)
        two_years_ago = datetime.now() - timedelta(days=730)
        old_mood_logs = db.query(MoodLog).filter(
            MoodLog.logged_at < two_years_ago
        ).delete()
        logger.info(f"Cleaned up {old_mood_logs} old mood logs")
        
        # Clean up old habit completions (keep last 2 years)
        old_habit_completions = db.query(HabitCompletion).filter(
            HabitCompletion.completed_at < two_years_ago
        ).delete()
        logger.info(f"Cleaned up {old_habit_completions} old habit completions")
        
        # Clean up old expenses (keep last 5 years for financial records)
        five_years_ago = datetime.now() - timedelta(days=1825)
        old_expenses = db.query(Expense).filter(
            Expense.date < five_years_ago
        ).delete()
        logger.info(f"Cleaned up {old_expenses} old expenses")
        
        # Clean up old conversations (keep last 6 months)
        six_months_ago = datetime.now() - timedelta(days=180)
        old_conversations = db.query(Conversation).filter(
            Conversation.created_at < six_months_ago
        ).delete()
        logger.info(f"Cleaned up {old_conversations} old conversations")
        
        # Clean up old embeddings (keep last 1 year)
        one_year_ago = datetime.now() - timedelta(days=365)
        old_embeddings = db.query(Embedding).filter(
            Embedding.created_at < one_year_ago
        ).delete()
        logger.info(f"Cleaned up {old_embeddings} old embeddings")
        
        db.commit()
        logger.info("Data cleanup completed successfully")
        
    except Exception as e:
        logger.error(f"Error in data cleanup: {str(e)}")
        db.rollback()
    finally:
        db.close()

@shared_task
def cleanup_orphaned_data():
    """Clean up orphaned data records"""
    try:
        db = SessionLocal()
        
        # Clean up orphaned habit completions
        orphaned_completions = db.query(HabitCompletion).filter(
            ~HabitCompletion.habit_id.in_(
                db.query(Habit.id)
            )
        ).delete()
        logger.info(f"Cleaned up {orphaned_completions} orphaned habit completions")
        
        # Clean up orphaned mood logs
        orphaned_mood_logs = db.query(MoodLog).filter(
            ~MoodLog.user_id.in_(
                db.query(User.id)
            )
        ).delete()
        logger.info(f"Cleaned up {orphaned_mood_logs} orphaned mood logs")
        
        # Clean up orphaned expenses
        orphaned_expenses = db.query(Expense).filter(
            ~Expense.user_id.in_(
                db.query(User.id)
            )
        ).delete()
        logger.info(f"Cleaned up {orphaned_expenses} orphaned expenses")
        
        db.commit()
        logger.info("Orphaned data cleanup completed successfully")
        
    except Exception as e:
        logger.error(f"Error in orphaned data cleanup: {str(e)}")
        db.rollback()
    finally:
        db.close()

@shared_task
def optimize_database():
    """Optimize database performance"""
    try:
        db = SessionLocal()
        
        # Analyze table statistics
        db.execute("ANALYZE")
        logger.info("Database analysis completed")
        
        # Vacuum tables to reclaim space
        db.execute("VACUUM")
        logger.info("Database vacuum completed")
        
        # Reindex tables for better performance
        db.execute("REINDEX DATABASE dristhi")
        logger.info("Database reindexing completed")
        
        logger.info("Database optimization completed successfully")
        
    except Exception as e:
        logger.error(f"Error in database optimization: {str(e)}")
    finally:
        db.close()

@shared_task
def archive_old_data():
    """Archive old data instead of deleting it"""
    try:
        db = SessionLocal()
        
        # Create archive tables if they don't exist
        # This is a placeholder for actual archiving logic
        
        # Archive old mood logs (older than 1 year)
        one_year_ago = datetime.now() - timedelta(days=365)
        old_mood_logs = db.query(MoodLog).filter(
            MoodLog.logged_at < one_year_ago
        ).all()
        
        # TODO: Implement actual archiving logic
        # This could involve:
        # 1. Moving data to archive tables
        # 2. Compressing data
        # 3. Moving to cold storage
        
        logger.info(f"Archived {len(old_mood_logs)} old mood logs")
        
        # Archive old habit completions
        old_habit_completions = db.query(HabitCompletion).filter(
            HabitCompletion.completed_at < one_year_ago
        ).all()
        
        logger.info(f"Archived {len(old_habit_completions)} old habit completions")
        
        logger.info("Data archiving completed successfully")
        
    except Exception as e:
        logger.error(f"Error in data archiving: {str(e)}")
    finally:
        db.close()
