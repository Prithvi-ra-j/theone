"""Career router for managing career goals, skills, and learning paths."""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.career import CareerGoal, Skill, LearningPath
from app.schemas.career import (
    CareerGoalCreate, CareerGoalRead, CareerGoalUpdate,
    SkillCreate, SkillRead, SkillUpdate,
    LearningPathCreate, LearningPathRead, LearningPathUpdate,
    CareerDashboard, SkillRecommendation
)
from app.routers.auth import get_current_user
from app.core.config import settings
from sqlalchemy.exc import IntegrityError

router = APIRouter()


# Career Goals
@router.post("/goals", response_model=CareerGoalRead, status_code=status.HTTP_201_CREATED)
async def create_career_goal(
    goal_data: CareerGoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new career goal."""
    # Ensure required DB fields have defaults in case the client omits them.
    goal_payload = goal_data.dict()
    if goal_payload.get("category") is None:
        goal_payload["category"] = "general"

    # Ensure we don't pass 'category' twice when expanding payload
    category_val = goal_payload.get("category") or "general"
    # Remove category from the payload so **goal_payload won't also provide it
    goal_payload.pop("category", None)

    # Explicitly pass category to ensure SQL INSERT receives a non-NULL value
    db_goal = CareerGoal(
        **goal_payload,
        user_id=current_user.id,
        category=category_val,
    )
    # Helpful debug log during development
    from loguru import logger
    logger.debug("Creating CareerGoal for user %s with payload: %s", current_user.id, goal_payload)

    # Defensive: ensure DB-required fields are present on the ORM object before commit.
    if getattr(db_goal, "category", None) is None:
        db_goal.category = "general"

    # Diagnostics: log DB URL, payload, and ORM state just before persisting so
    # we can trace why a NULL might be inserted into the category column.
    logger.info("Using DATABASE_URL: %s", getattr(settings, "DATABASE_URL", "<unset>"))
    logger.info("CareerGoal payload before add: %s", goal_payload)
    logger.info("db_goal.category before add: %s", getattr(db_goal, "category", None))

    # Also query information_schema for the runtime nullability of the column
    # to verify the database schema from the same DB connection.
    try:
        info = db.execute(
            "SELECT is_nullable FROM information_schema.columns WHERE table_name='careergoal' AND column_name='category';"
        ).fetchone()
        logger.debug("information_schema.category.is_nullable = %s", info)
    except Exception as _e:
        logger.debug("Could not query information_schema: %s", _e)

    db.add(db_goal)
    try:
        db.commit()
        db.refresh(db_goal)
    except IntegrityError as exc:
        # Log and raise a clear HTTP error with helpful debugging info.
        logger.error("IntegrityError while creating CareerGoal: %s", exc)
        # Attempt to include the DB column nullability in the error if we have it
        try:
            info = db.execute(
                "SELECT is_nullable FROM information_schema.columns WHERE table_name='careergoal' AND column_name='category';"
            ).fetchone()
        except Exception:
            info = None
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "IntegrityError",
                "message": str(exc.orig) if getattr(exc, "orig", None) else str(exc),
                "db_url": str(getattr(settings, "DATABASE_URL", "<unset>")),
                "payload": goal_payload,
                "db_goal_category": getattr(db_goal, "category", None),
                "information_schema_category": info,
            },
        )
    except Exception as exc:  # pragma: no cover - unexpected runtime error
        logger.exception("Unexpected error creating CareerGoal: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "UnexpectedError",
                "message": str(exc),
                "db_url": str(getattr(settings, "DATABASE_URL", "<unset>")),
                "payload": goal_payload,
            },
        )

    # Validate and return a Pydantic model instance while the DB session
    # is still active to avoid FastAPI response validation errors that can
    # occur when returned ORM objects are partially unloaded.
    return CareerGoalRead.model_validate(db_goal)


@router.get("/goals", response_model=List[CareerGoalRead])
async def get_career_goals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    status_filter: str = "all",
    limit: int = 20,
    offset: int = 0
) -> Any:
    """Get all career goals for the current user."""
    query = db.query(CareerGoal).filter(CareerGoal.user_id == current_user.id)
    if status_filter != "all":
        query = query.filter(CareerGoal.status == status_filter)
    goals = query.order_by(CareerGoal.created_at.desc()).offset(offset).limit(limit).all()
    return goals


@router.get("/goals/{goal_id}", response_model=CareerGoalRead)
async def get_career_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get a specific career goal."""
    goal = db.query(CareerGoal).filter(
        CareerGoal.id == goal_id,
        CareerGoal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career goal not found"
        )
    
    return goal


@router.put("/goals/{goal_id}", response_model=CareerGoalRead)
async def update_career_goal(
    goal_id: int,
    goal_update: CareerGoalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update a career goal."""
    goal = db.query(CareerGoal).filter(
        CareerGoal.id == goal_id,
        CareerGoal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career goal not found"
        )
    
    # Update fields
    for field, value in goal_update.dict(exclude_unset=True).items():
        setattr(goal, field, value)
    
    db.commit()
    db.refresh(goal)
    return goal


@router.delete("/goals/{goal_id}")
async def delete_career_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Delete a career goal."""
    goal = db.query(CareerGoal).filter(
        CareerGoal.id == goal_id,
        CareerGoal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career goal not found"
        )
    
    db.delete(goal)
    db.commit()
    
    return {"message": "Career goal deleted successfully"}


# Skills
@router.post("/skills", response_model=SkillRead, status_code=status.HTTP_201_CREATED)
async def create_skill(
    skill_data: SkillCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new skill."""
    db_skill = Skill(
        **skill_data.dict(),
        user_id=current_user.id
    )
    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)
    return db_skill


@router.get("/skills", response_model=List[SkillRead])
async def get_skills(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    category: str = None,
    limit: int = 20,
    offset: int = 0
) -> Any:
    """Get all skills for the current user."""
    query = db.query(Skill).filter(Skill.user_id == current_user.id)
    if category:
        query = query.filter(Skill.category == category)
    skills = query.order_by(Skill.name).offset(offset).limit(limit).all()
    return skills


@router.get("/skills/{skill_id}", response_model=SkillRead)
async def get_skill(
    skill_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get a specific skill."""
    skill = db.query(Skill).filter(
        Skill.id == skill_id,
        Skill.user_id == current_user.id
    ).first()
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    
    return skill


@router.put("/skills/{skill_id}", response_model=SkillRead)
async def update_skill(
    skill_id: int,
    skill_update: SkillUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update a skill."""
    skill = db.query(Skill).filter(
        Skill.id == skill_id,
        Skill.user_id == current_user.id
    ).first()
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    
    # Update fields
    for field, value in skill_update.dict(exclude_unset=True).items():
        setattr(skill, field, value)
    
    db.commit()
    db.refresh(skill)
    return skill


@router.delete("/skills/{skill_id}")
async def delete_skill(
    skill_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Delete a skill."""
    skill = db.query(Skill).filter(
        Skill.id == skill_id,
        Skill.user_id == current_user.id
    ).first()
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    
    db.delete(skill)
    db.commit()
    
    return {"message": "Skill deleted successfully"}


# Learning Paths
@router.post("/learning-paths", response_model=LearningPathRead, status_code=status.HTTP_201_CREATED)
async def create_learning_path(
    path_data: LearningPathCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new learning path."""
    # Verify skill exists and belongs to user
    skill = db.query(Skill).filter(
        Skill.id == path_data.skill_id,
        Skill.user_id == current_user.id
    ).first()
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    
    db_path = LearningPath(
        **path_data.dict(),
        user_id=current_user.id
    )
    db.add(db_path)
    db.commit()
    db.refresh(db_path)
    return db_path


@router.get("/learning-paths", response_model=List[LearningPathRead])
async def get_learning_paths(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    status: str = None,
    limit: int = 20,
    offset: int = 0
) -> Any:
    """Get all learning paths for the current user."""
    query = db.query(LearningPath).filter(LearningPath.user_id == current_user.id)
    if status:
        query = query.filter(LearningPath.status == status)
    paths = query.order_by(LearningPath.created_at.desc()).offset(offset).limit(limit).all()
    return paths


@router.put("/learning-paths/{path_id}", response_model=LearningPathRead)
async def update_learning_path(
    path_id: int,
    path_update: LearningPathUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update a learning path."""
    path = db.query(LearningPath).filter(
        LearningPath.id == path_id,
        LearningPath.user_id == current_user.id
    ).first()
    
    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning path not found"
        )
    
    # Update fields
    for field, value in path_update.dict(exclude_unset=True).items():
        setattr(path, field, value)
    
    db.commit()
    db.refresh(path)
    return path


# Dashboard
@router.get("/dashboard", response_model=CareerDashboard)
async def get_career_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get career dashboard data."""
    # Get goals
    goals = db.query(CareerGoal).filter(CareerGoal.user_id == current_user.id).all()
    total_goals = len(goals)
    active_goals = len([g for g in goals if g.status == "active"])
    completed_goals = len([g for g in goals if g.status == "completed"])
    
    # Get skills
    skills = db.query(Skill).filter(Skill.user_id == current_user.id).all()
    total_skills = len(skills)
    skills_in_progress = len([s for s in skills if s.current_level < s.target_level])
    average_skill_level = sum(s.current_level for s in skills) / total_skills if total_skills > 0 else 0
    
    # Get learning paths
    learning_paths = db.query(LearningPath).filter(LearningPath.user_id == current_user.id).all()
    
    return CareerDashboard(
        user_id=current_user.id,
        total_goals=total_goals,
        active_goals=active_goals,
        completed_goals=completed_goals,
        total_skills=total_skills,
        skills_in_progress=skills_in_progress,
        average_skill_level=round(average_skill_level, 1),
        recent_goals=goals[:5],  # Last 5 goals
        top_skills=sorted(skills, key=lambda x: x.current_level, reverse=True)[:5],  # Top 5 skills
        learning_paths=learning_paths[:5]  # Last 5 learning paths
    )


# AI Recommendations (placeholder)
@router.get("/recommendations", response_model=List[SkillRecommendation])
async def get_skill_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get AI-generated skill recommendations."""
    # TODO: Implement AI-powered skill recommendations
    # For MVP, return placeholder data
    return [
        SkillRecommendation(
            skill_name="Python Advanced",
            description="Advanced Python programming concepts",
            category="technical",
            reason="Based on your current Python level and career goals",
            priority="high",
            estimated_effort="40 hours",
            related_skills=["Data Structures", "Algorithms", "Web Development"],
            learning_resources=["Python.org", "Real Python", "LeetCode"]
        )
    ]
