"""Celery configuration for Dristhi backend."""

import os
from celery import Celery
from app.core.config import settings

# Create Celery instance
celery_app = Celery(
    "dristhi",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.ai_insights",
        "app.tasks.habit_reminders", 
        "app.tasks.finance_alerts",
        "app.tasks.motivation_messages",
        "app.tasks.data_cleanup"
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    result_expires=3600,  # 1 hour
    task_always_eager=settings.DEBUG,  # Execute tasks synchronously in debug mode
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=True,
    task_ignore_result=False,
)

# Celery beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "daily-habit-reminders": {
        "task": "app.tasks.habit_reminders.send_daily_habit_reminders",
        "schedule": 60.0 * 60.0 * 24.0,  # Daily
    },
    "daily-motivation": {
        "task": "app.tasks.motivation_messages.send_daily_motivation",
        "schedule": 60.0 * 60.0 * 24.0,  # Daily
    },
    "weekly-finance-summary": {
        "task": "app.tasks.finance_alerts.send_weekly_finance_summary",
        "schedule": 60.0 * 60.0 * 24.0 * 7.0,  # Weekly
    },
    "weekly-ai-insights": {
        "task": "app.tasks.ai_insights.generate_weekly_insights",
        "schedule": 60.0 * 60.0 * 24.0 * 7.0,  # Weekly
    },
    "monthly-data-cleanup": {
        "task": "app.tasks.data_cleanup.cleanup_old_data",
        "schedule": 60.0 * 60.0 * 24.0 * 30.0,  # Monthly
    },
}

if __name__ == "__main__":
    celery_app.start()