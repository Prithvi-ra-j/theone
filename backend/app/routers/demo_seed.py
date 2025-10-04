"""Demo seeding endpoints to populate the database for a prototype demo."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Any
from datetime import datetime, timedelta

from app.db.session import get_db
from app.routers.auth import get_current_user
from app.models.user import User
from app.models.career import CareerGoal, Skill, LearningPath, LearningPathMilestone, LearningPathProject
from app.models.habits import Habit, Task as HabitTask
from app.models.finance import FinancialGoal
from app.models.mood import MoodLog
from app.models.gamification import UserStats
from app.models.mini_assistant import MiniAssistant, AssistantInteraction

router = APIRouter(prefix="/demo", tags=["demo"])


@router.post("/seed", response_model=dict)
async def seed_demo(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Populate the current (demo) user with sample data across features."""
    # Mini Assistant
    assistant = db.query(MiniAssistant).filter(MiniAssistant.user_id == current_user.id).first()
    if not assistant:
        assistant = MiniAssistant(
            user_id=current_user.id,
            name="Astra",
            avatar="🪔",
            personality="mentor",
            color_theme="blue",
            greeting_message="Hi! I'm here to help you grow, one step at a time.",
            preferences={"notifications": True}
        )
        db.add(assistant)
        db.flush()
        db.add(AssistantInteraction(
            assistant_id=assistant.id,
            user_id=current_user.id,
            interaction_type="greeting",
            content=assistant.greeting_message,
        ))

    # Career goals
    if db.query(CareerGoal).filter(CareerGoal.user_id == current_user.id).count() == 0:
        g1 = CareerGoal(
            user_id=current_user.id,
            title="Become a Full-Stack Developer",
            description="Build strong skills in React, Node, and databases",
            category="technical",
            priority="high",
            status="active",
        )
        g2 = CareerGoal(
            user_id=current_user.id,
            title="Earn AWS Associate Certification",
            description="Pass the AWS SAA-C03 exam",
            category="certification",
            priority="medium",
            status="active",
        )
        db.add_all([g1, g2])
        db.flush()

    # Skills
    existing_skills = {s.name.lower() for s in db.query(Skill).filter(Skill.user_id == current_user.id).all()}
    for name, cat, cur, tgt, core in [
        ("React", "technical", "intermediate", "advanced", True),
        ("Python", "technical", "advanced", "expert", True),
        ("Time Management", "soft_skills", "beginner", "intermediate", False),
    ]:
        if name.lower() not in existing_skills:
            db.add(Skill(
                user_id=current_user.id,
                name=name,
                category=cat,
                current_level=cur,
                target_level=tgt,
                is_priority=core,
            ))

    # Learning Path
    skill = db.query(Skill).filter(Skill.user_id == current_user.id).first()
    if skill and db.query(LearningPath).filter(LearningPath.user_id == current_user.id).count() == 0:
        lp = LearningPath(
            user_id=current_user.id,
            title="Full-Stack Foundations",
            description="A 6-week intensive path",
            field="web_development",
            difficulty_level="beginner",
            estimated_duration_weeks=6,
            current_milestone="Week 1: HTML/CSS",
        )
        db.add(lp)
        db.flush()
        # Seed milestones
        milestones = [
            ("Foundations", "HTML, CSS basics", 1),
            ("JavaScript Core", "JS syntax and DOM", 2),
            ("Frontend Project", "Build a small site", 3),
            ("Backend Basics", "APIs with Node/Python", 4),
            ("Full-Stack Project", "Combine frontend+backend", 5),
            ("Capstone", "Deploy and present", 6),
        ]
        for idx, (t, d, w) in enumerate(milestones, start=1):
            db.add(LearningPathMilestone(
                learning_path_id=lp.id,
                title=t,
                description=d,
                order_index=idx,
                estimated_weeks=w,
                status="planned",
            ))
        # Seed projects
        db.add(LearningPathProject(
            learning_path_id=lp.id,
            title="Portfolio Website",
            description="Responsive site with 3 pages",
            order_index=1,
            est_hours=10,
            status="planned",
        ))
        db.add(LearningPathProject(
            learning_path_id=lp.id,
            title="Full-Stack Capstone",
            description="Clone a simple real-world app",
            order_index=2,
            est_hours=20,
            status="planned",
        ))

    # Habits and tasks
    if db.query(Habit).filter(Habit.user_id == current_user.id).count() == 0:
        db.add(Habit(
            user_id=current_user.id,
            name="Daily Coding",
            description="Code 1 hour",
            category="productivity",
            frequency="daily",
            target_value=60,
            unit="minutes",
        ))
    if db.query(HabitTask).filter(HabitTask.user_id == current_user.id).count() == 0:
        db.add(HabitTask(
            user_id=current_user.id,
            title="Review PRs",
            description="Review 2 pull requests",
            priority="medium",
        ))

    # Finance
    if db.query(FinancialGoal).filter(FinancialGoal.user_id == current_user.id).count() == 0:
        db.add(FinancialGoal(
            user_id=current_user.id,
            title="Save for Laptop",
            description="MacBook for development",
            goal_type="savings",
            target_amount=80000.0,
            current_amount=25000.0,
            status="active",
            priority="medium",
            monthly_contribution=5000.0,
        ))

    # Mood entries
    if db.query(MoodLog).filter(MoodLog.user_id == current_user.id).count() == 0:
        for i in range(5):
            db.add(MoodLog(
                user_id=current_user.id,
                mood_score=7 + (i % 3),
                notes=f"Feeling day {i+1}",
                logged_at=datetime.utcnow() - timedelta(days=i)
            ))

    # Gamification
    stats = db.query(UserStats).filter(UserStats.user_id == current_user.id).first()
    if not stats:
        stats = UserStats(
            user_id=current_user.id,
            total_points=120,
            current_level=3,
            points_to_next_level=400,
            current_login_streak=4,
            longest_login_streak=4,
            total_habits_completed=5,
            total_tasks_completed=3,
            total_mood_logs=5,
            total_expenses_logged=2,
        )
        db.add(stats)

    db.commit()
    return {"status": "ok", "message": "Demo data seeded"}
