"""Mood router for wellness tracking and mood logging."""

from typing import Any, List
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.models.user import User
from app.models.mood import MoodLog
from app.routers.auth import get_current_user

router = APIRouter()


@router.post("/log", response_model=dict, status_code=status.HTTP_201_CREATED)
async def log_mood(
    mood_score: int,
    mood_label: str = None,
    energy_level: int = None,
    stress_level: int = None,
    sleep_hours: float = None,
    exercise_minutes: int = None,
    notes: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Log a new mood entry."""
    # Validate mood score
    if not 1 <= mood_score <= 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mood score must be between 1 and 10"
        )
    
    db_mood = MoodLog(
        user_id=current_user.id,
        mood_score=mood_score,
        mood_label=mood_label,
        energy_level=energy_level,
        stress_level=stress_level,
        sleep_hours=sleep_hours,
        exercise_minutes=exercise_minutes,
        notes=notes
    )
    db.add(db_mood)
    db.commit()
    db.refresh(db_mood)
    return {"message": "Mood logged successfully", "mood_id": db_mood.id}


@router.get("/logs", response_model=List[dict])
async def get_mood_logs(
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get mood logs for the specified number of days."""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    logs = db.query(MoodLog).filter(
        MoodLog.user_id == current_user.id,
        MoodLog.date >= start_date
    ).order_by(MoodLog.date.desc()).all()
    
    return [
        {
            "id": log.id,
            "mood_score": log.mood_score,
            "mood_label": log.mood_label,
            "energy_level": log.energy_level,
            "stress_level": log.stress_level,
            "sleep_hours": log.sleep_hours,
            "exercise_minutes": log.exercise_minutes,
            "notes": log.notes,
            "date": log.date
        }
        for log in logs
    ]


@router.get("/dashboard")
async def get_mood_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get mood dashboard data."""
    # Get current week's data
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    # Average mood score
    avg_mood = db.query(func.avg(MoodLog.mood_score)).filter(
        MoodLog.user_id == current_user.id,
        MoodLog.date >= week_ago
    ).scalar() or 0
    
    # Average energy level
    avg_energy = db.query(func.avg(MoodLog.energy_level)).filter(
        MoodLog.user_id == current_user.id,
        MoodLog.date >= week_ago,
        MoodLog.energy_level.isnot(None)
    ).scalar() or 0
    
    # Average stress level
    avg_stress = db.query(func.avg(MoodLog.stress_level)).filter(
        MoodLog.user_id == current_user.id,
        MoodLog.date >= week_ago,
        MoodLog.stress_level.isnot(None)
    ).scalar() or 0
    
    # Average sleep hours
    avg_sleep = db.query(func.avg(MoodLog.sleep_hours)).filter(
        MoodLog.user_id == current_user.id,
        MoodLog.date >= week_ago,
        MoodLog.sleep_hours.isnot(None)
    ).scalar() or 0
    
    # Mood trends (last 7 days)
    daily_moods = db.query(
        func.date(MoodLog.date).label('date'),
        func.avg(MoodLog.mood_score).label('avg_mood')
    ).filter(
        MoodLog.user_id == current_user.id,
        MoodLog.date >= week_ago
    ).group_by(func.date(MoodLog.date)).all()
    
    return {
        "weekly_averages": {
            "mood_score": round(float(avg_mood), 1),
            "energy_level": round(float(avg_energy), 1),
            "stress_level": round(float(avg_stress), 1),
            "sleep_hours": round(float(avg_sleep), 1)
        },
        "mood_trends": [
            {
                "date": str(date),
                "avg_mood": round(float(avg_mood), 1)
            }
            for date, avg_mood in daily_moods
        ],
        "wellness_score": round((float(avg_mood) + float(avg_energy) + (10 - float(avg_stress))) / 3, 1)
    }


@router.get("/insights")
async def get_mood_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get AI-generated mood insights."""
    # For MVP, return placeholder insights
    # In production, this would use the AI service
    
    return {
        "insights": [
            {
                "type": "mood_pattern",
                "title": "Your mood tends to be higher on weekends",
                "description": "Consider planning enjoyable activities during weekdays to maintain consistent mood levels."
            },
            {
                "type": "sleep_quality",
                "title": "Better sleep correlates with higher mood scores",
                "description": "Focus on maintaining a consistent sleep schedule for improved well-being."
            },
            {
                "type": "exercise_impact",
                "title": "Exercise days show 20% higher energy levels",
                "description": "Even 15 minutes of daily exercise can significantly boost your energy and mood."
            }
        ],
        "recommendations": [
            "Try to maintain consistent sleep hours",
            "Include short exercise sessions in your daily routine",
            "Practice stress management techniques like meditation",
            "Track your mood patterns to identify triggers"
        ]
    }
