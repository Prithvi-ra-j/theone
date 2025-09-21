"""Mood router for wellness tracking and mood logging."""

from typing import Any, List, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.models.user import User
from app.models.mood import MoodLog
from app.routers.auth import get_current_user, get_optional_current_user

router = APIRouter()


@router.post("/log", response_model=dict, status_code=status.HTTP_201_CREATED)
async def log_mood(
    payload: dict = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Log a new mood entry."""
    # Extract fields from JSON payload and validate/cast
    mood_score = payload.get('mood_score')
    # map incoming 'mood_label' to model's primary_emotion
    mood_label = payload.get('mood_label')
    primary_emotion = payload.get('primary_emotion') or mood_label
    energy_level = payload.get('energy_level')
    stress_level = payload.get('stress_level')
    sleep_hours = payload.get('sleep_hours')
    exercise_minutes = payload.get('exercise_minutes')
    notes = payload.get('notes')

    if mood_score is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="mood_score is required")

    try:
        mood_score = int(mood_score)
    except Exception:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="mood_score must be an integer between 1 and 10")

    if not 1 <= mood_score <= 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mood score must be between 1 and 10"
        )

    # Optional numeric casts
    try:
        energy_level = int(energy_level) if energy_level is not None else None
    except Exception:
        energy_level = None
    try:
        stress_level = int(stress_level) if stress_level is not None else None
    except Exception:
        stress_level = None
    try:
        sleep_hours = float(sleep_hours) if sleep_hours is not None else None
    except Exception:
        sleep_hours = None
    try:
        exercise_minutes = int(exercise_minutes) if exercise_minutes is not None else None
    except Exception:
        exercise_minutes = None

    db_mood = MoodLog(
        user_id=current_user.id,
        mood_score=mood_score,
        primary_emotion=primary_emotion,
        energy_level=energy_level,
        stress_level=stress_level,
        sleep_hours=sleep_hours,
        exercise_minutes=exercise_minutes,
        notes=notes,
        logged_at=datetime.utcnow()
    )
    db.add(db_mood)
    db.commit()
    db.refresh(db_mood)
    return {"message": "Mood logged successfully", "mood_id": db_mood.id}


@router.get("/logs", response_model=List[dict])
async def get_mood_logs(
    days: int = 7,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get mood logs for the specified number of days."""
    start_date = datetime.utcnow() - timedelta(days=days)

    # Use `log_date` (model column) and compare against date portion of start_date
    query = db.query(MoodLog).filter(MoodLog.log_date >= start_date.date())
    if current_user is not None:
        query = query.filter(MoodLog.user_id == current_user.id)
    logs = query.order_by(MoodLog.log_date.desc()).all()
    
    return [
        {
            "id": log.id,
            "mood_score": log.mood_score,
            "primary_emotion": getattr(log, 'primary_emotion', None),
            "energy_level": log.energy_level,
            "stress_level": log.stress_level,
            "sleep_hours": log.sleep_hours,
            "exercise_minutes": log.exercise_minutes,
            "notes": log.notes,
            "date": log.log_date,
            "logged_at": getattr(log, 'logged_at', None)
        }
        for log in logs
    ]


@router.get("/dashboard")
async def get_mood_dashboard(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get mood dashboard data."""
    # Get current week's data
    week_ago = datetime.utcnow() - timedelta(days=7)

    base_filters = [MoodLog.log_date >= week_ago]
    if current_user is not None:
        base_filters.insert(0, MoodLog.user_id == current_user.id)

    # Average mood score (MoodLog uses `log_date` and `logged_at`)
    avg_mood = db.query(func.avg(MoodLog.mood_score)).filter(*base_filters).scalar() or 0
    
    # Average energy level
    energy_filters = [MoodLog.log_date >= week_ago, MoodLog.energy_level.isnot(None)]
    if current_user is not None:
        energy_filters.insert(0, MoodLog.user_id == current_user.id)
    avg_energy = db.query(func.avg(MoodLog.energy_level)).filter(*energy_filters).scalar() or 0
    
    # Average stress level
    stress_filters = [MoodLog.log_date >= week_ago, MoodLog.stress_level.isnot(None)]
    if current_user is not None:
        stress_filters.insert(0, MoodLog.user_id == current_user.id)
    avg_stress = db.query(func.avg(MoodLog.stress_level)).filter(*stress_filters).scalar() or 0
    
    # Average sleep hours
    sleep_filters = [MoodLog.log_date >= week_ago, MoodLog.sleep_hours.isnot(None)]
    if current_user is not None:
        sleep_filters.insert(0, MoodLog.user_id == current_user.id)
    avg_sleep = db.query(func.avg(MoodLog.sleep_hours)).filter(*sleep_filters).scalar() or 0
    
    # Mood trends (last 7 days)
    # Group by log_date (the model column name). Use func.date on log_date
    # to produce a day bucket for trends.
    daily_filters = [MoodLog.log_date >= week_ago]
    if current_user is not None:
        daily_filters.insert(0, MoodLog.user_id == current_user.id)
    daily_moods = db.query(
        func.date(MoodLog.log_date).label('date'),
        func.avg(MoodLog.mood_score).label('avg_mood')
    ).filter(*daily_filters).group_by(func.date(MoodLog.log_date)).all()
    
    return {
        "weekly_averages": {
            "mood_score": round(float(avg_mood), 1),
            "energy_level": round(float(avg_energy), 1),
            "stress_level": round(float(avg_stress), 1),
            "sleep_hours": round(float(avg_sleep), 1)
        },
        "mood_trends": [
            {
                "date": str(day),
                "avg_mood": round(float(avg_m), 1)
            }
            for day, avg_m in daily_moods
        ],
        "wellness_score": round((float(avg_mood) + float(avg_energy) + (10 - float(avg_stress))) / 3, 1)
    }


@router.get("/insights")
async def get_mood_insights(
    current_user: Optional[User] = Depends(get_optional_current_user),
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
