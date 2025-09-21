from celery import shared_task
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.finance import Expense, Budget, FinancialGoal
from app.models.user import User
from sqlalchemy import func
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_weekly_finance_summary():
    """Send weekly finance summary to users"""
    try:
        db = SessionLocal()
        
        # Get all users
        users = db.query(User).all()
        
        for user in users:
            try:
                # Calculate weekly expenses
                week_ago = datetime.now() - timedelta(days=7)
                weekly_expenses = db.query(func.sum(Expense.amount)).filter(
                    Expense.user_id == user.id,
                    Expense.date >= week_ago
                ).scalar() or 0
                
                # Get budget information
                budgets = db.query(Budget).filter(
                    Budget.user_id == user.id,
                    Budget.is_active == True
                ).all()
                
                # Check for budget overruns
                budget_alerts = []
                for budget in budgets:
                    if budget.amount < weekly_expenses:
                        budget_alerts.append(f"Budget '{budget.name}' exceeded by {weekly_expenses - budget.amount}")
                
                # Generate summary message
                summary_message = f"Weekly Finance Summary:\nExpenses: {weekly_expenses}\n"
                if budget_alerts:
                    summary_message += f"Alerts: {', '.join(budget_alerts)}"
                
                logger.info(f"Sending weekly finance summary to user {user.id}")
                
                # TODO: Implement actual notification sending
                
            except Exception as e:
                logger.error(f"Error processing finance summary for user {user.id}: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"Error in weekly finance summary: {str(e)}")
    finally:
        db.close()

@shared_task
def check_budget_overruns():
    """Check for budget overruns and send alerts"""
    try:
        db = SessionLocal()
        
        # Get all active budgets
        active_budgets = db.query(Budget).filter(Budget.is_active == True).all()
        
        for budget in active_budgets:
            try:
                # Calculate current month expenses
                month_start = datetime.now().replace(day=1)
                monthly_expenses = db.query(func.sum(Expense.amount)).filter(
                    Expense.user_id == budget.user_id,
                    Expense.date >= month_start
                ).scalar() or 0
                
                # Check if over budget
                if monthly_expenses > budget.amount:
                    user = db.query(User).filter(User.id == budget.user_id).first()
                    if user:
                        alert_message = f"Budget Alert: You've exceeded your '{budget.name}' budget by {monthly_expenses - budget.amount}"
                        logger.info(f"Sending budget overrun alert to user {user.id}")
                        
                        # TODO: Implement actual notification sending
                        
            except Exception as e:
                logger.error(f"Error processing budget overrun for budget {budget.id}: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"Error in budget overrun check: {str(e)}")
    finally:
        db.close()

@shared_task
def send_financial_goal_updates():
    """Send updates on financial goal progress"""
    try:
        db = SessionLocal()
        
        # Get all financial goals
        financial_goals = db.query(FinancialGoal).all()
        
        for goal in financial_goals:
            try:
                # Calculate progress percentage
                if goal.target_amount > 0:
                    progress = (goal.current_amount / goal.target_amount) * 100
                    # Prefer title, fall back to legacy name attribute
                    goal_label = getattr(goal, 'title', None) or getattr(goal, 'name', None) or 'your'
                    
                    # Send milestone alerts
                    if progress >= 25 and progress < 30:
                        milestone_message = f"Great progress! You're 25% towards your '{goal_label}' goal!"
                    elif progress >= 50 and progress < 55:
                        milestone_message = f"Halfway there! You've reached 50% of your '{goal_label}' goal!"
                    elif progress >= 75 and progress < 80:
                        milestone_message = f"Almost there! You're 75% towards your '{goal_label}' goal!"
                    elif progress >= 100:
                        milestone_message = f"Congratulations! You've achieved your '{goal_label}' goal!"
                    else:
                        continue
                    
                    user = db.query(User).filter(User.id == goal.user_id).first()
                    if user:
                        logger.info(f"Sending financial goal milestone to user {user.id}")
                        
                        # TODO: Implement actual notification sending
                        
            except Exception as e:
                logger.error(f"Error processing financial goal update for goal {goal.id}: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"Error in financial goal updates: {str(e)}")
    finally:
        db.close()
