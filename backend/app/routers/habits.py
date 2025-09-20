"""Habits router for managing habits, tasks, and calendar events."""

from typing import Any, List
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.habits import Habit, HabitCompletion, Task, CalendarEvent
from app.routers.auth import get_current_user

router = APIRouter()


# Habits
@router.post("/habits", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_habit(
    name: str,
    description: str = None,
    frequency: str = "daily",
    target_count: int = 1,
    reminder_time: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new habit."""
    db_habit = Habit(
        user_id=current_user.id,
        name=name,
        description=description,
        frequency=frequency,
        target_count=target_count,
        reminder_time=reminder_time
    )
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)
    return {"message": "Habit created successfully", "habit_id": db_habit.id}


@router.get("/habits", response_model=List[dict])
async def get_habits(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get all habits for the current user."""
    habits = db.query(Habit).filter(Habit.user_id == current_user.id).all()
    return [
        {
            "id": habit.id,
            "name": habit.name,
            "description": habit.description,
            "frequency": habit.frequency,
            "target_count": habit.target_count,
            "current_streak": habit.current_streak,
            "longest_streak": habit.longest_streak,
            "is_active": habit.is_active
        }
        for habit in habits
    ]


@router.post("/habits/{habit_id}/complete")
async def complete_habit(
    habit_id: int,
    notes: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Mark a habit as completed for today."""
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
@router.post("/habits/tasks", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_task(
    title: str,
    description: str = None,
    due_date: str = None,
    priority: str = "medium",
    category: str = None,
    estimated_minutes: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new task."""
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
@router.get("/habits/tasks", response_model=List[dict])
async def get_tasks(
    status: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get all tasks for the current user."""
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
@router.put("/habits/tasks/{task_id}/status")
async def update_task_status(
    task_id: int,
    new_status: str,
    current_user: User = Depends(get_current_user),
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
@router.post("/habits/events", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_event(
    title: str,
    description: str = None,
    start_datetime: str = None,
    end_datetime: str = None,
    location: str = None,
    is_all_day: bool = False,
    reminder_minutes: int = 15,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new calendar event."""
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
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return {"message": "Event created successfully", "event_id": db_event.id}


@router.get("/events", response_model=List[dict])
@router.get("/habits/events", response_model=List[dict])
async def get_events(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get all calendar events for the current user."""
    events = db.query(CalendarEvent).filter(
        CalendarEvent.user_id == current_user.id
    ).order_by(CalendarEvent.start_datetime).all()
    
    return [
        {
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "start_datetime": event.start_datetime,
            "end_datetime": event.end_datetime,
            "location": event.location,
            "all_day": event.all_day
        }
        for event in events
    ]


# Dashboard
@router.get("/dashboard")
async def get_habits_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get habits dashboard data."""
    # Get habits
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
    
    return {
        "total_habits": len(habits),
        "habits_completed_today": len(today_completions),
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
            "total_streak": sum(habit.current_streak for habit in habits),
            "longest_streak": max((habit.longest_streak for habit in habits), default=0)
        }
    }
