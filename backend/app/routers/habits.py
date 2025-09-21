"""Habits router for managing habits, tasks, and calendar events."""

from typing import Any, List, Optional
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.habits import Habit, HabitCompletion, Task, CalendarEvent
from app.routers.auth import get_current_user, get_optional_current_user

router = APIRouter()


# Habits
@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_habit(
    payload: dict = Body(...),
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new habit. Accepts JSON body payload."""
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    name = payload.get('name')
    if not name:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='name is required')
    description = payload.get('description')
    frequency = payload.get('frequency', 'daily')
    # Model uses `target_value` (float) and `unit` rather than `target_count`.
    # Accept either `target_value` or `target_count` from older clients.
    raw_target = payload.get('target_value', payload.get('target_count'))
    try:
        target_value = float(raw_target) if raw_target is not None else None
    except Exception:
        target_value = None

    unit = payload.get('unit')
    # category is required by the model; default to 'general' when not provided
    category = payload.get('category', 'general')
    reminder_time = payload.get('reminder_time')

    db_habit = Habit(
        user_id=current_user.id,
        name=name,
        description=description,
        category=category,
        frequency=frequency,
        target_value=target_value,
        unit=unit,
        reminder_time=reminder_time
    )
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)
    return {"message": "Habit created successfully", "habit_id": db_habit.id}


@router.get("/", response_model=List[dict])
async def get_habits(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get all habits for the current user."""
    if current_user is None:
        return []
    habits = db.query(Habit).filter(Habit.user_id == current_user.id).all()
    return [
        {
            "id": habit.id,
            "name": habit.name,
            "description": habit.description,
            "frequency": habit.frequency,
            "target_value": habit.target_value,
            "unit": habit.unit,
            "current_streak": habit.current_streak,
            "longest_streak": habit.longest_streak,
            "is_active": habit.is_active
        }
        for habit in habits
    ]


@router.post("/{habit_id}/complete")
async def complete_habit(
    habit_id: int,
    payload: dict = Body({}),
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Mark a habit as completed for today."""
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id
    ).first()
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    
    # Check if already completed today
    today = date.today()
    existing_completion = db.query(HabitCompletion).filter(
        HabitCompletion.habit_id == habit_id,
        HabitCompletion.completed_date == today
    ).first()
    
    if existing_completion:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Habit already completed today"
        )
    
    # Create completion record
    notes = payload.get('notes')
    completion = HabitCompletion(
        habit_id=habit_id,
        user_id=current_user.id,
        notes=notes
    )
    db.add(completion)
    
    # Update streak
    habit.current_streak += 1
    if habit.current_streak > habit.longest_streak:
        habit.longest_streak = habit.current_streak
    
    db.commit()
    
    return {"message": "Habit completed successfully", "current_streak": habit.current_streak}


# Tasks
@router.post("/tasks", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: dict = Body(...),
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new task. Accepts JSON body payload."""
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    title = payload.get('title')
    if not title:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='title is required')
    description = payload.get('description')
    due_date = payload.get('due_date')
    priority = payload.get('priority', 'medium')
    category = payload.get('category')
    estimated_minutes = payload.get('estimated_minutes')

    db_task = Task(
        user_id=current_user.id,
        title=title,
        description=description,
        due_date=due_date,
        priority=priority,
        category=category,
        estimated_minutes=estimated_minutes
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return {"message": "Task created successfully", "task_id": db_task.id}


@router.get("/tasks", response_model=List[dict])
async def get_tasks(
    status: str = None,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get all tasks for the current user."""
    if current_user is None:
        return []
    query = db.query(Task).filter(Task.user_id == current_user.id)
    
    if status:
        query = query.filter(Task.status == status)
    
    tasks = query.order_by(Task.created_at.desc()).all()
    return [
        {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "category": task.category,
            "due_date": task.due_date,
            "estimated_minutes": task.estimated_minutes
        }
        for task in tasks
    ]


@router.put("/tasks/{task_id}/status")
async def update_task_status(
    task_id: int,
    new_status: str,
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update task status."""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    task.status = new_status
    if new_status == "completed":
        task.completed_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Task status updated successfully"}


# Calendar Events
@router.post("/events", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_event(
    payload: dict = Body(...),
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new calendar event. Accepts JSON body payload."""
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    title = payload.get('title')
    if not title:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='title is required')

    description = payload.get('description')
    start_dt_raw = payload.get('start_datetime')
    end_dt_raw = payload.get('end_datetime')
    location = payload.get('location')
    is_all_day = bool(payload.get('is_all_day', False))
    reminder_minutes = payload.get('reminder_minutes', 15)

    # Validate required datetimes
    if not start_dt_raw or not end_dt_raw:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='start_datetime and end_datetime are required')

    # Parse ISO date/time strings into datetime objects when necessary
    try:
        if isinstance(start_dt_raw, str):
            start_datetime = datetime.fromisoformat(start_dt_raw)
        else:
            start_datetime = start_dt_raw

        if isinstance(end_dt_raw, str):
            end_datetime = datetime.fromisoformat(end_dt_raw)
        else:
            end_datetime = end_dt_raw
    except Exception:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Invalid datetime format. Use ISO-8601 strings.')

    try:
        reminder_minutes = int(reminder_minutes or 15)
    except Exception:
        reminder_minutes = 15

    db_event = CalendarEvent(
        user_id=current_user.id,
        title=title,
        description=description,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        location=location,
        all_day=is_all_day,
        reminder_time=reminder_minutes
    )
    try:
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create event: {e}")

    return {"message": "Event created successfully", "event_id": db_event.id}


@router.get("/events", response_model=List[dict])
async def get_events(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get all calendar events for the current user."""
    if current_user is None:
        return []
    events = db.query(CalendarEvent).filter(
        CalendarEvent.user_id == current_user.id
    ).order_by(CalendarEvent.start_datetime).all()
    
    return [
        {
            "id": event.id,
            "title": event.title,
            "description": event.description,
            # Provide both legacy-friendly keys and canonical datetime fields.
            "start_datetime": event.start_datetime,
            "end_datetime": event.end_datetime,
            # Frontend expects `start_time`/`end_time` (date-only or ISO strings).
            "start_time": event.start_datetime.isoformat() if getattr(event, 'start_datetime', None) is not None else None,
            "end_time": event.end_datetime.isoformat() if getattr(event, 'end_datetime', None) is not None else None,
            "location": event.location,
            "all_day": event.all_day
        }
        for event in events
    ]


# Dashboard
@router.get("/dashboard")
async def get_habits_dashboard(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get habits dashboard data."""
    # Get habits
    if current_user is None:
        return {
            "total_habits": 0,
            "habits_completed_today": 0,
            "pending_tasks": 0,
            "upcoming_events": [],
            "streak_summary": {"total_streak": 0, "longest_streak": 0}
        }
    habits = db.query(Habit).filter(
        Habit.user_id == current_user.id,
        Habit.is_active == True
    ).all()
    
    # Get today's completions
    today = date.today()
    today_completions = db.query(HabitCompletion).filter(
        HabitCompletion.user_id == current_user.id,
        HabitCompletion.completed_date == today
    ).all()
    
    # Get pending tasks
    pending_tasks = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.status == "pending"
    ).count()
    
    # Get upcoming events
    upcoming_events = db.query(CalendarEvent).filter(
        CalendarEvent.user_id == current_user.id,
        CalendarEvent.start_datetime >= datetime.utcnow()
    ).order_by(CalendarEvent.start_datetime).limit(5).all()
    # Build today_habits list expected by the frontend
    completed_habit_ids = {c.habit_id for c in today_completions}
    today_habits = [
        {
            "id": habit.id,
            "name": habit.name,
            "description": habit.description,
            "category": habit.category,
            "frequency": habit.frequency,
            "target_value": habit.target_value,
            "unit": habit.unit,
            "current_streak": habit.current_streak,
            "longest_streak": habit.longest_streak,
            "is_active": habit.is_active,
            "is_completed": habit.id in completed_habit_ids
        }
        for habit in habits
    ]

    # Frontend expects keys like `completed_habits_today` and `current_streak`.
    # Keep `streak_summary` for backward compatibility but expose the more
    # directly used keys as well.
    total_habits = len(habits)
    completed_habits_today = len(today_completions)
    streak_total = sum(habit.current_streak for habit in habits)
    longest_streak = max((habit.longest_streak for habit in habits), default=0)

    return {
        "total_habits": total_habits,
        "completed_habits_today": completed_habits_today,
        "pending_tasks": pending_tasks,
        "upcoming_events": [
            {
                "title": event.title,
                "start_datetime": event.start_datetime,
                "location": event.location
            }
            for event in upcoming_events
        ],
        "streak_summary": {
            "total_streak": streak_total,
            "longest_streak": longest_streak
        },
        # Convenience keys expected by the frontend
        "current_streak": streak_total,
        "today_habits": today_habits,
    }
