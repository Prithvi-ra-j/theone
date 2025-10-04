"""Mini Assistant router for managing user's personalized assistant."""

from typing import Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.mini_assistant import MiniAssistant, AssistantInteraction
from app.routers.auth import get_current_user, get_optional_current_user
from pydantic import BaseModel, Field

router = APIRouter()


# Pydantic models for request/response
class MiniAssistantBase(BaseModel):
    name: str
    avatar: str
    personality: str
    color_theme: Optional[str] = None
    greeting_message: Optional[str] = None
    preferences: Optional[dict] = None


class MiniAssistantCreate(MiniAssistantBase):
    pass


class MiniAssistantUpdate(MiniAssistantBase):
    pass


class MiniAssistantRead(MiniAssistantBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class InteractionBase(BaseModel):
    interaction_type: str
    content: str
    metadata: Optional[dict] = None


class InteractionCreate(InteractionBase):
    pass


class InteractionRead(InteractionBase):
    id: int
    assistant_id: int
    user_id: int
    is_read: bool
    created_at: datetime

    class Config:
        orm_mode = True


class NudgeResponse(BaseModel):
    message: str
    action_suggestion: str | None = None
    related_feature: str | None = None


class ToolSpec(BaseModel):
    name: str
    title: str
    description: str
    params: dict


class ToolExecuteRequest(BaseModel):
    tool: str = Field(..., description="Tool name (e.g., career.create_goal)")
    params: dict = Field(default_factory=dict)


class ToolExecuteResponse(BaseModel):
    ok: bool
    tool: str
    result: dict | None = None
    error: str | None = None


class BulkDeleteRequest(BaseModel):
    ids: List[int]


# API Endpoints
# Note: This router is included with prefix "/api/v1/mini-assistant" in app.main,
# so the paths here should be relative to that (e.g., "/" instead of "/mini-assistant").
@router.post("/", response_model=MiniAssistantRead)
@router.post("", response_model=MiniAssistantRead, include_in_schema=False)
async def create_mini_assistant(
    assistant: MiniAssistantCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new mini assistant for the current user."""
    # Check if user already has an assistant
    existing = db.query(MiniAssistant).filter(
        MiniAssistant.user_id == current_user.id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a mini assistant"
        )
    
    # Create new assistant
    db_assistant = MiniAssistant(
        user_id=current_user.id,
        name=assistant.name,
        avatar=assistant.avatar,
        personality=assistant.personality,
        color_theme=assistant.color_theme,
        greeting_message=assistant.greeting_message,
        preferences=assistant.preferences
    )
    
    db.add(db_assistant)
    db.commit()
    db.refresh(db_assistant)
    
    # Create initial greeting interaction
    greeting = f"Hello {current_user.name}! I'm {assistant.name}, your personal assistant. I'm here to help you achieve your goals."
    
    interaction = AssistantInteraction(
        assistant_id=db_assistant.id,
        user_id=current_user.id,
        interaction_type="greeting",
        content=greeting
    )
    
    db.add(interaction)
    db.commit()
    
    return db_assistant


@router.get("/", response_model=MiniAssistantRead)
@router.get("", response_model=MiniAssistantRead, include_in_schema=False)
async def get_mini_assistant(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get the current user's mini assistant."""
    assistant = db.query(MiniAssistant).filter(
        MiniAssistant.user_id == current_user.id
    ).first()
    
    if not assistant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mini assistant not found"
        )
    
    return assistant


@router.put("/", response_model=MiniAssistantRead)
@router.put("", response_model=MiniAssistantRead, include_in_schema=False)
async def update_mini_assistant(
    assistant: MiniAssistantUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update the current user's mini assistant."""
    db_assistant = db.query(MiniAssistant).filter(
        MiniAssistant.user_id == current_user.id
    ).first()
    
    if not db_assistant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mini assistant not found"
        )
    
    # Update fields
    db_assistant.name = assistant.name
    db_assistant.avatar = assistant.avatar
    db_assistant.personality = assistant.personality
    db_assistant.color_theme = assistant.color_theme
    db_assistant.greeting_message = assistant.greeting_message
    db_assistant.preferences = assistant.preferences
    db_assistant.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_assistant)
    
    return db_assistant


@router.post("/interactions", response_model=InteractionRead)
async def create_interaction(
    interaction: InteractionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new interaction with the mini assistant."""
    # Get user's assistant
    assistant = db.query(MiniAssistant).filter(
        MiniAssistant.user_id == current_user.id
    ).first()
    
    if not assistant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mini assistant not found"
        )
    
    # Create interaction
    db_interaction = AssistantInteraction(
        assistant_id=assistant.id,
        user_id=current_user.id,
        interaction_type=interaction.interaction_type,
        content=interaction.content,
        interaction_metadata=interaction.metadata
    )
    
    db.add(db_interaction)
    db.commit()
    db.refresh(db_interaction)
    # Map ORM field interaction_metadata -> API field metadata
    return {
        "id": db_interaction.id,
        "assistant_id": db_interaction.assistant_id,
        "user_id": db_interaction.user_id,
        "interaction_type": db_interaction.interaction_type,
        "content": db_interaction.content,
        "metadata": db_interaction.interaction_metadata,
        "is_read": db_interaction.is_read,
        "created_at": db_interaction.created_at,
    }


@router.get("/interactions", response_model=List[InteractionRead])
async def get_interactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 10,
    offset: int = 0
) -> Any:
    """Get the current user's interactions with their mini assistant."""
    # Get user's assistant
    assistant = db.query(MiniAssistant).filter(
        MiniAssistant.user_id == current_user.id
    ).first()
    
    if not assistant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mini assistant not found"
        )
    
    # Get interactions
    interactions = db.query(AssistantInteraction).filter(
        AssistantInteraction.user_id == current_user.id,
        AssistantInteraction.assistant_id == assistant.id
    ).order_by(AssistantInteraction.created_at.desc()).offset(offset).limit(limit).all()
    # Map interaction_metadata -> metadata for response
    return [
        {
            "id": i.id,
            "assistant_id": i.assistant_id,
            "user_id": i.user_id,
            "interaction_type": i.interaction_type,
            "content": i.content,
            "metadata": i.interaction_metadata,
            "is_read": i.is_read,
            "created_at": i.created_at,
        }
        for i in interactions
    ]


@router.post("/interactions/bulk-delete")
async def bulk_delete_interactions(
    req: BulkDeleteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Hard-delete multiple interactions belonging to the current user's assistant."""
    if not req.ids:
        return {"deleted": 0}

    assistant = db.query(MiniAssistant).filter(
        MiniAssistant.user_id == current_user.id
    ).first()

    if not assistant:
        raise HTTPException(status_code=404, detail="Mini assistant not found")

    q = db.query(AssistantInteraction).filter(
        AssistantInteraction.id.in_(req.ids),
        AssistantInteraction.user_id == current_user.id,
        AssistantInteraction.assistant_id == assistant.id,
    )
    # Count via subquery since delete() returns rowcount depending on backend
    to_delete = q.all()
    deleted = len(to_delete)
    for it in to_delete:
        db.delete(it)
    db.commit()
    return {"deleted": deleted}


@router.post("/interactions/delete-all")
async def delete_all_interactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Delete all interactions for the current user's assistant."""
    assistant = db.query(MiniAssistant).filter(
        MiniAssistant.user_id == current_user.id
    ).first()

    if not assistant:
        raise HTTPException(status_code=404, detail="Mini assistant not found")

    q = db.query(AssistantInteraction).filter(
        AssistantInteraction.user_id == current_user.id,
        AssistantInteraction.assistant_id == assistant.id,
    )
    # Fetch for count then delete
    items = q.all()
    count = len(items)
    for it in items:
        db.delete(it)
    db.commit()
    return {"deleted": count}


@router.put("/interactions/{interaction_id}/read")
async def mark_interaction_as_read(
    interaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Mark an interaction as read."""
    interaction = db.query(AssistantInteraction).filter(
        AssistantInteraction.id == interaction_id,
        AssistantInteraction.user_id == current_user.id
    ).first()
    
    if not interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interaction not found"
        )
    
    interaction.is_read = True
    db.commit()
    
    return {"status": "success"}


@router.post("/interactions/read")
async def mark_all_interactions_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Mark all interactions for the current user's assistant as read (used by frontend)."""
    assistant = db.query(MiniAssistant).filter(
        MiniAssistant.user_id == current_user.id
    ).first()

    if not assistant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mini assistant not found"
        )

    db.query(AssistantInteraction).filter(
        AssistantInteraction.user_id == current_user.id,
        AssistantInteraction.assistant_id == assistant.id,
        AssistantInteraction.is_read == False
    ).update({AssistantInteraction.is_read: True})
    db.commit()

    return {"status": "success"}


@router.get("/nudge", response_model=NudgeResponse)
async def get_nudge(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Provide a simple contextual nudge based on recent memory and assistant settings (MVP)."""
    try:
        # Pull a bit of context via MemoryService if available
        from app.services.memory_service import MemoryService
        ms = MemoryService()
        context_items = ms.search_memories(user_id=current_user.id, query="goal", top_k=1)
        context_snippet = context_items[0]["content"] if context_items else None
    except Exception:
        context_snippet = None

    # Use user's assistant preferences if set
    personality = getattr(current_user, "assistant_personality", None) or "mentor"
    avatar = getattr(current_user, "assistant_avatar", None) or "diya"
    language = getattr(current_user, "assistant_language", None) or "english"

    # Default MVP message
    base_msg = "Keep up the momentum! Take one small step today."
    if context_snippet:
        base_msg = f"About your goal: {context_snippet}. Consider a quick 15-minute action today."

    message = f"[{avatar}] ({personality}) {base_msg}"
    action = "Open your Career tasks"
    related = "career"

    # Optional enhancement: attempt to use AI for a richer personalized nudge
    try:
        from app.services.ai_service import AIService
        ai = AIService()
        if not ai.is_available:
            # Attempt lazy initialization; ignore failures
            import asyncio as _asyncio
            try:
                # If we're not in an event loop, run initialize synchronously
                loop = _asyncio.get_running_loop()
                # If in a running loop, schedule and ignore result
                _ = _asyncio.create_task(ai.initialize())
            except RuntimeError:
                # No running loop; run a new event loop for init
                _asyncio.run(ai.initialize())

        if ai.is_available and getattr(ai, "llm", None) is not None:
            prompt = (
                "You are a friendly, concise productivity coach. Given the user's recent context (optional), "
                "generate a single short nudge (<= 25 words) in the specified language and tone. "
                "End with a concrete next action suggestion.\n"
                f"Tone/personality: {personality}. Language: {language}.\n"
                f"Context: {context_snippet or 'N/A'}."
            )
            try:
                if callable(ai.llm):
                    out = ai.llm(prompt)
                elif hasattr(ai.llm, "invoke"):
                    out = ai.llm.invoke(prompt)
                else:
                    out = None
                if out:
                    # Use AI text as the message, keep action/related defaults
                    message = f"[{avatar}] ({personality}) {str(out).strip()}"
            except Exception:
                pass
    except Exception:
        # Ignore AI errors; return fallback message
        pass

    return NudgeResponse(
        message=message,
        action_suggestion=action,
        related_feature=related,
    )


@router.get("/tools", response_model=list[ToolSpec])
async def list_tools() -> Any:
    """Return a small catalog of allowed assistant tools and their parameters."""
    return [
        ToolSpec(
            name="career.create_goal",
            title="Create Career Goal",
            description="Create a new career goal for the user.",
            params={
                "title": {"type": "string", "required": True},
                "description": {"type": "string", "required": False},
                "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"], "required": False},
                "target_date": {"type": "string", "format": "date-time", "required": False},
            },
        ),
        ToolSpec(
            name="career.add_skill",
            title="Add Skill",
            description="Add a new skill to your profile.",
            params={
                "name": {"type": "string", "required": True},
                "category": {"type": "string", "required": False},
                "current_level": {"type": "string", "enum": ["beginner", "intermediate", "advanced", "expert"], "required": False},
                "proficiency_score": {"type": "number", "required": False},
            },
        ),
        ToolSpec(
            name="career.start_learning_path",
            title="Start Learning Path",
            description="Start (or create and start) a learning path.",
            params={
                "learning_path_id": {"type": "number", "required": False},
                "title": {"type": "string", "required": False},
                "field": {"type": "string", "required": False},
                "difficulty_level": {"type": "string", "enum": ["beginner", "intermediate", "advanced"], "required": False},
                "start_date": {"type": "string", "format": "date-time", "required": False},
            },
        ),
        ToolSpec(
            name="habits.complete_today",
            title="Complete Habit Today",
            description="Mark a habit as completed for today.",
            params={
                "habit_id": {"type": "integer", "required": True},
                "notes": {"type": "string", "required": False},
            },
        ),
        ToolSpec(
            name="habits.create_habit",
            title="Create Habit",
            description="Create a new habit.",
            params={
                "name": {"type": "string", "required": True},
                "category": {"type": "string", "required": False},
                "frequency": {"type": "string", "enum": ["daily", "weekly"], "required": False},
                "target_value": {"type": "number", "required": False},
                "unit": {"type": "string", "required": False},
            },
        ),
        ToolSpec(
            name="finance.add_expense",
            title="Add Expense",
            description="Create a new expense record.",
            params={
                "amount": {"type": "number", "required": True},
                "category": {"type": "string", "required": True},
                "description": {"type": "string", "required": True},
            },
        ),
        ToolSpec(
            name="finance.create_budget",
            title="Create Budget",
            description="Create a budget for a category.",
            params={
                "name": {"type": "string", "required": False},
                "amount": {"type": "number", "required": True},
                "category": {"type": "string", "required": True},
                "period_type": {"type": "string", "enum": ["weekly", "monthly", "yearly"], "required": False},
                "start_date": {"type": "string", "format": "date-time", "required": False},
                "end_date": {"type": "string", "format": "date-time", "required": False},
            },
        ),
        ToolSpec(
            name="mood.log",
            title="Log Mood",
            description="Log your current mood and optional wellness details.",
            params={
                "mood_score": {"type": "number", "required": True},
                "primary_emotion": {"type": "string", "required": False},
                "energy_level": {"type": "number", "required": False},
                "stress_level": {"type": "number", "required": False},
                "sleep_hours": {"type": "number", "required": False},
                "exercise_minutes": {"type": "number", "required": False},
                "notes": {"type": "string", "required": False},
            },
        ),
        ToolSpec(
            name="finance.create_income",
            title="Add Income",
            description="Create a new income record.",
            params={
                "amount": {"type": "number", "required": True},
                "source": {"type": "string", "required": True},
                "description": {"type": "string", "required": False},
                "date_received": {"type": "string", "format": "date-time", "required": False},
                "is_recurring": {"type": "string", "enum": ["true", "false"], "required": False},
                "recurring_frequency": {"type": "string", "enum": ["weekly", "monthly", "yearly"], "required": False},
                "is_taxable": {"type": "string", "enum": ["true", "false"], "required": False},
                "tax_amount": {"type": "number", "required": False},
            },
        ),
        ToolSpec(
            name="journal.create_entry",
            title="Add Journal Entry",
            description="Create a journal entry and trigger AI analysis.",
            params={
                "content": {"type": "string", "required": True},
                "tags": {"type": "array", "items": {"type": "string"}, "required": False},
                "user_mood": {"type": "number", "required": False},
                "is_private": {"type": "boolean", "required": False},
            },
        ),
    ]


@router.post("/tools/execute", response_model=ToolExecuteResponse)
async def execute_tool(
    req: ToolExecuteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Execute a whitelisted tool on behalf of the user. Keep scope narrow and auditable."""
    try:
        if req.tool == "career.create_goal":
            from app.models.career import CareerGoal
            title = (req.params or {}).get("title")
            if not title:
                raise HTTPException(status_code=422, detail="title is required")
            description = (req.params or {}).get("description")
            priority = (req.params or {}).get("priority") or "medium"
            target_date_raw = (req.params or {}).get("target_date")
            target_dt = None
            if target_date_raw:
                try:
                    from datetime import datetime as _dt
                    target_dt = _dt.fromisoformat(str(target_date_raw))
                except Exception:
                    target_dt = None
            goal = CareerGoal(
                user_id=current_user.id,
                title=title,
                description=description,
                priority=priority,
                target_date=target_dt,
            )
            db.add(goal)
            db.commit()
            db.refresh(goal)
            return ToolExecuteResponse(ok=True, tool=req.tool, result={"goal_id": goal.id, "title": goal.title})

        if req.tool == "career.add_skill":
            from app.models.career import Skill
            name = (req.params or {}).get("name")
            if not name:
                raise HTTPException(status_code=422, detail="name is required")
            category = (req.params or {}).get("category") or "technical"
            current_level = (req.params or {}).get("current_level") or "beginner"
            prof = (req.params or {}).get("proficiency_score")
            try:
                proficiency_score = float(prof) if prof is not None else 0.0
            except Exception:
                proficiency_score = 0.0
            skill = Skill(
                user_id=current_user.id,
                name=name,
                category=category,
                current_level=current_level,
                proficiency_score=proficiency_score,
            )
            db.add(skill)
            db.commit()
            db.refresh(skill)
            return ToolExecuteResponse(ok=True, tool=req.tool, result={"skill_id": skill.id, "name": skill.name})

        if req.tool == "career.start_learning_path":
            from datetime import datetime as _dt
            from app.models.career import LearningPath
            lp_id = (req.params or {}).get("learning_path_id")
            start_raw = (req.params or {}).get("start_date")
            start_dt = None
            if start_raw:
                try:
                    start_dt = _dt.fromisoformat(str(start_raw))
                except Exception:
                    start_dt = None
            if lp_id:
                lp = db.query(LearningPath).filter(LearningPath.id == lp_id, LearningPath.user_id == current_user.id).first()
                if not lp:
                    raise HTTPException(status_code=404, detail="Learning path not found")
                lp.started_at = start_dt or _dt.utcnow()
                db.commit()
                return ToolExecuteResponse(ok=True, tool=req.tool, result={"learning_path_id": lp.id, "started_at": str(lp.started_at)})
            # else create and start new
            title = (req.params or {}).get("title") or "My Learning Path"
            field = (req.params or {}).get("field") or "general"
            difficulty_level = (req.params or {}).get("difficulty_level") or "beginner"
            lp = LearningPath(
                user_id=current_user.id,
                title=title,
                field=field,
                difficulty_level=difficulty_level,
                started_at=start_dt or _dt.utcnow(),
                is_active=True,
            )
            db.add(lp)
            db.commit()
            db.refresh(lp)
            return ToolExecuteResponse(ok=True, tool=req.tool, result={"learning_path_id": lp.id, "title": lp.title})

        if req.tool == "habits.complete_today":
            from datetime import date as _date
            from app.models.habits import Habit, HabitCompletion
            habit_id = (req.params or {}).get("habit_id")
            if not habit_id:
                raise HTTPException(status_code=422, detail="habit_id is required")
            habit = db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == current_user.id).first()
            if not habit:
                raise HTTPException(status_code=404, detail="Habit not found")
            today = _date.today()
            exists = db.query(HabitCompletion).filter(
                HabitCompletion.habit_id == habit_id,
                HabitCompletion.user_id == current_user.id,
                HabitCompletion.completed_date == today,
            ).first()
            if exists:
                return ToolExecuteResponse(ok=True, tool=req.tool, result={"message": "Already completed"})
            notes = (req.params or {}).get("notes")
            completion = HabitCompletion(habit_id=habit_id, user_id=current_user.id, notes=notes)
            db.add(completion)
            habit.current_streak += 1
            if habit.current_streak > habit.longest_streak:
                habit.longest_streak = habit.current_streak
            db.commit()
            return ToolExecuteResponse(ok=True, tool=req.tool, result={"current_streak": habit.current_streak})

        if req.tool == "habits.create_habit":
            from app.models.habits import Habit
            name = (req.params or {}).get("name")
            if not name:
                raise HTTPException(status_code=422, detail="name is required")
            category = (req.params or {}).get("category") or "general"
            frequency = (req.params or {}).get("frequency") or "daily"
            unit = (req.params or {}).get("unit")
            tv = (req.params or {}).get("target_value")
            try:
                target_value = float(tv) if tv is not None else None
            except Exception:
                target_value = None
            hb = Habit(
                user_id=current_user.id,
                name=name,
                category=category,
                frequency=frequency,
                unit=unit,
                target_value=target_value,
            )
            db.add(hb)
            db.commit()
            db.refresh(hb)
            return ToolExecuteResponse(ok=True, tool=req.tool, result={"habit_id": hb.id})

        if req.tool == "finance.add_expense":
            from app.models.finance import Expense
            try:
                amount = float((req.params or {}).get("amount"))
            except Exception:
                raise HTTPException(status_code=422, detail="amount is required and must be a number")
            category = (req.params or {}).get("category")
            description = (req.params or {}).get("description")
            if not category or not description:
                raise HTTPException(status_code=422, detail="category and description are required")
            exp = Expense(
                user_id=current_user.id,
                amount=amount,
                category=category,
                description=description,
            )
            db.add(exp)
            db.commit()
            db.refresh(exp)
            return ToolExecuteResponse(ok=True, tool=req.tool, result={"expense_id": exp.id})

        if req.tool == "finance.create_budget":
            from datetime import datetime as _dt
            from app.models.finance import Budget
            name = (req.params or {}).get("name") or "Budget"
            try:
                amount = float((req.params or {}).get("amount"))
            except Exception:
                raise HTTPException(status_code=422, detail="amount is required and must be a number")
            category = (req.params or {}).get("category")
            if not category:
                raise HTTPException(status_code=422, detail="category is required")
            period_type = (req.params or {}).get("period_type") or "monthly"
            sd = (req.params or {}).get("start_date")
            ed = (req.params or {}).get("end_date")
            try:
                start_date = _dt.fromisoformat(str(sd)) if sd else _dt.utcnow()
            except Exception:
                start_date = _dt.utcnow()
            try:
                end_date = _dt.fromisoformat(str(ed)) if ed else _dt.utcnow()
            except Exception:
                end_date = _dt.utcnow()
            b = Budget(
                user_id=current_user.id,
                name=name,
                amount=amount,
                category=category,
                period_type=period_type,
                start_date=start_date,
                end_date=end_date,
            )
            db.add(b)
            db.commit()
            db.refresh(b)
            return ToolExecuteResponse(ok=True, tool=req.tool, result={"budget_id": b.id})

        if req.tool == "mood.log":
            from datetime import datetime as _dt
            from app.models.mood import MoodLog
            params = req.params or {}
            mood_score = params.get("mood_score")
            if mood_score is None:
                raise HTTPException(status_code=422, detail="mood_score is required")
            try:
                mood_score = int(mood_score)
            except Exception:
                raise HTTPException(status_code=422, detail="mood_score must be an integer between 1 and 10")
            if not 1 <= mood_score <= 10:
                raise HTTPException(status_code=400, detail="Mood score must be between 1 and 10")
            def _to_int(v):
                try:
                    return int(v) if v is not None else None
                except Exception:
                    return None
            def _to_float(v):
                try:
                    return float(v) if v is not None else None
                except Exception:
                    return None
            ml = MoodLog(
                user_id=current_user.id,
                mood_score=mood_score,
                primary_emotion=params.get("primary_emotion"),
                energy_level=_to_int(params.get("energy_level")),
                stress_level=_to_int(params.get("stress_level")),
                sleep_hours=_to_float(params.get("sleep_hours")),
                exercise_minutes=_to_int(params.get("exercise_minutes")),
                notes=params.get("notes"),
                logged_at=_dt.utcnow(),
            )
            db.add(ml)
            db.commit()
            db.refresh(ml)
            return ToolExecuteResponse(ok=True, tool=req.tool, result={"mood_id": ml.id})

        if req.tool == "finance.create_income":
            from datetime import datetime as _dt
            from app.models.finance import Income
            params = req.params or {}
            try:
                amount = float(params.get("amount"))
            except Exception:
                raise HTTPException(status_code=422, detail="amount is required and must be a number")
            source = params.get("source")
            if not source:
                raise HTTPException(status_code=422, detail="source is required")
            desc = params.get("description")
            date_received_raw = params.get("date_received")
            date_received = None
            if date_received_raw:
                try:
                    date_received = _dt.fromisoformat(str(date_received_raw)).date()
                except Exception:
                    date_received = None
            def _to_bool(v):
                if isinstance(v, bool):
                    return v
                if v is None:
                    return None
                return str(v).strip().lower() in ("true", "1", "yes", "on")
            is_recurring = _to_bool(params.get("is_recurring")) or False
            recurring_frequency = params.get("recurring_frequency")
            is_taxable = _to_bool(params.get("is_taxable"))
            try:
                tax_amount = float(params.get("tax_amount")) if params.get("tax_amount") is not None else None
            except Exception:
                tax_amount = None
            inc = Income(
                user_id=current_user.id,
                amount=amount,
                source=source,
                description=desc,
                date_received=date_received or _dt.utcnow().date(),
                is_recurring=is_recurring,
                recurring_frequency=recurring_frequency,
                is_taxable=is_taxable if is_taxable is not None else True,
                tax_amount=tax_amount,
            )
            db.add(inc)
            db.commit()
            db.refresh(inc)
            return ToolExecuteResponse(ok=True, tool=req.tool, result={"income_id": inc.id})

        if req.tool == "journal.create_entry":
            params = req.params or {}
            content = (params.get("content") or "").strip()
            if not content:
                raise HTTPException(status_code=422, detail="content is required")
            tags = params.get("tags") or []
            user_mood = params.get("user_mood")
            is_private = bool(params.get("is_private", True))

            from app.models.journal import JournalEntry, JournalAnalysis
            entry = JournalEntry(
                user_id=current_user.id,
                content=content,
                tags=tags,
                user_mood=user_mood,
                is_private=is_private,
            )
            db.add(entry)
            db.commit()
            db.refresh(entry)

            # Best-effort analysis similar to the journal router
            try:
                from app.services.ai_service import AIService
                from app.services.memory_service import MemoryService
                ai = AIService()
                if not ai.is_available:
                    await ai.initialize()
                analysis_data = {
                    "mood_score": 0,
                    "valence": None,
                    "arousal": None,
                    "emotions": [{"label": "neutral", "score": 0.5}],
                    "topics": None,
                    "triggers": None,
                    "suggestions": None,
                    "keywords": None,
                    "summary": content[:160],
                    "safety_flags": None,
                }
                try:
                    if getattr(ai, "llm", None) is not None:
                        import json
                        prompt = (
                            "Analyze the following journal entry and return a compact JSON with fields: "
                            "mood_score(-5..5), valence(0..1), arousal(0..1), emotions([{'label','score'}]), "
                            "topics([str]), triggers([str]), suggestions([str]), keywords([str]), summary(str), safety_flags([str]).\n"
                            f"Text: {content}"
                        )
                        raw = ai.llm.invoke(prompt)
                        parsed = json.loads(str(raw)) if raw else {}
                        analysis_data.update({k: parsed.get(k) for k in analysis_data.keys()})
                except Exception:
                    pass
                ja = JournalAnalysis(journal_id=entry.id, **analysis_data)
                db.add(ja)
                db.commit()
                db.refresh(ja)
                try:
                    ms = MemoryService()
                    snippet = ja.summary or content[:200]
                    ms.store_memory(user_id=current_user.id, content=snippet, memory_type="journal", metadata={"journal_id": entry.id, "tags": tags})
                except Exception:
                    pass
            except Exception:
                pass
            return ToolExecuteResponse(ok=True, tool=req.tool, result={"entry_id": entry.id})

        # Unknown tool
        raise HTTPException(status_code=404, detail="Unknown tool")
    except HTTPException:
        raise
    except Exception as e:
        return ToolExecuteResponse(ok=False, tool=req.tool, error=str(e))


@router.post("/stream")
async def stream_assistant_response(
    payload: dict = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Stream a response in chunks for a ChatGPT-like typing effect (MVP)."""
    prompt = str(payload.get("prompt") or payload.get("message") or "")
    if not prompt:
        raise HTTPException(status_code=400, detail="prompt is required")

    include_context = bool(payload.get("include_context", False))
    context_type = str(payload.get("context_type") or "general")
    route_hint = str(payload.get("route") or "")

    # Build an optional short context preamble via MemoryService
    context_preamble = ""
    if include_context:
        try:
            from app.services.memory_service import MemoryService
            ms = MemoryService()
            ctx = ms.get_user_context(current_user.id, context_type=context_type, max_memories=5)
            # Summarize minimally to keep stream snappy
            goals = ", ".join((ctx.get("career_progress", {}).get("current_goals") or [])[:3])
            skills = ", ".join((ctx.get("career_progress", {}).get("skills_in_progress") or [])[:3])
            habits = ", ".join((ctx.get("habits") or [])[:3])
            prefs = ctx.get("preferences") or {}
            name = prefs.get("name") or "user"
            context_preamble = (
                f"Context for {name}: "
                f"Goals: {goals or '—'}; Skills: {skills or '—'}; Habits: {habits or '—'}; Route: {route_hint or '—'}. "
            )
        except Exception:
            context_preamble = ""

    # Load assistant profile for a nicer greeting
    assistant = db.query(MiniAssistant).filter(
        MiniAssistant.user_id == current_user.id
    ).first()

    def _is_greeting(text: str) -> bool:
        t = (text or "").strip().lower()
        if not t:
            return False
        # normalize
        for ch in ",.!?":
            t = t.replace(ch, "")
        short = len(t.split()) <= 6 and len(t) <= 30
        greetings = {"hi", "hello", "hey", "yo", "hiya", "sup", "hey there", "hi there"}
        return short and (t in greetings or any(t.startswith(g + " ") for g in greetings))

    def _build_greeting() -> str:
        # Best-effort name from context preamble (already built) or fallback to user's email prefix
        user_name = None
        try:
            # crude parse "Context for NAME: "
            if context_preamble.startswith("Context for "):
                seg = context_preamble[len("Context for ") :].split(":", 1)[0].strip()
                user_name = seg if seg and seg != "user" else None
        except Exception:
            user_name = None
        if not user_name:
            try:
                user_name = getattr(current_user, "name", None) or (current_user.email.split("@")[0] if getattr(current_user, "email", None) else None)
            except Exception:
                user_name = None

        a_name = assistant.name if assistant and getattr(assistant, "name", None) else "Assistant"
        persona = assistant.personality if assistant and getattr(assistant, "personality", None) else "helpful"

        hello = f"Hey {user_name}!" if user_name else "Hey there!"
        intro = f"I'm {a_name}, your {persona} AI assistant."
        suggestions = (
            "Here are a few things you can try right now:\n"
            "- Ask me anything (“What should I focus on this week?”)\n"
            "- Draft a message or plan (“Help me write a concise email about …”)\n"
            "- Use tools: log mood, track a habit, add an expense or income\n"
            "- Summarize context (“Summarize my current goals and next steps”)"
        )
        tip = "Tip: You can toggle context on/off at the top anytime."
        return f"{hello} {intro}\n\n{suggestions}\n\n{tip}"

    import asyncio
    from functools import partial
    import re

    # Quick intent recognizers
    def _is_add_expense(text: str) -> bool:
        t = (text or "").lower()
        return any(ph in t for ph in ["add expense", "log expense", "record expense", "i spent", "added an expense"])  # basic patterns

    def _parse_expense(text: str):
        """Return (amount: float|None, category: str|None, description: str|None).
        Tries to detect amount like Rs/₹/$ 123.45 and category after 'on' or 'for'."""
        if not text:
            return None, None, None
        # amount
        amt = None
        m = re.search(r"(?:rs\.?|₹|\$)?\s*([0-9]+(?:\.[0-9]{1,2})?)", text, flags=re.IGNORECASE)
        if m:
            try:
                amt = float(m.group(1))
            except Exception:
                amt = None
        # category: word after 'on' or 'for'
        cat = None
        m2 = re.search(r"\b(?:on|for)\s+([a-zA-Z\-_/]+)", text, flags=re.IGNORECASE)
        if m2:
            cat = m2.group(1).strip().lower()
        # description: rest of sentence after category cue
        desc = None
        if cat:
            after = re.split(r"\b(?:on|for)\s+" + re.escape(cat), text, flags=re.IGNORECASE)
            if len(after) > 1:
                desc = after[1].strip(" .,-:")
        # fallback: if quotes present
        if not desc:
            m3 = re.search(r"['\"]([^'\"]{3,})['\"]", text)
            if m3:
                desc = m3.group(1).strip()
        return amt, cat, desc

    def _template_wrap(user_text: str, ctx_snippets: list[str]) -> str:
        ctx_block = "\n".join(f"- {s}" for s in ctx_snippets) if ctx_snippets else "- (No additional context used)"
        return (
            "## Overview\n"
            f"{user_text}\n\n"
            "## Next 3 Steps\n"
            "- [ ] Step 1\n"
            "- [ ] Step 2\n"
            "- [ ] Step 3\n\n"
            "## 3 Resources\n"
            "1. Title — link\n"
            "2. Title — link\n"
            "3. Title — link\n\n"
            "## Risks / Watchouts\n"
            "- Risk 1\n"
            "- Risk 2\n\n"
            "---\n"
            "Context used:\n"
            f"{ctx_block}\n"
        )

    # Prepare minimal RAG: retrieve top 3 memory snippets similar to prompt
    rag_snippets: list[str] = []
    try:
        from app.services.memory_service import MemoryService
        ms = MemoryService()
        retrieved = ms.search_memories(user_id=current_user.id, query=prompt, top_k=3) or []
        # Expect items like {id, content, ...}
        for r in retrieved:
            content = r.get("content") or ""
            ident = r.get("id") or r.get("uuid")
            label = f"[{ident}] {content[:140]}" if ident else content[:140]
            if label:
                rag_snippets.append(label)
    except Exception:
        rag_snippets = []

    async def _call_llm(ai, final_prompt: str) -> str:
        # offload synchronous invoke to thread and allow timeout protection
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, partial(ai.llm.invoke, final_prompt))

    async def event_gen():
        # Try AI service; otherwise stream a simple echo with delay
        try:
            from app.services.ai_service import AIService
            ai = AIService()
            if not ai.is_available:
                await ai.initialize()
            # 1) Tool-like intents handled first for better UX
            if _is_add_expense(prompt):
                amt, cat, desc = _parse_expense(prompt)
                # If required fields missing, ask concise follow-up instead of generic template
                if amt is None or not cat or not desc:
                    msg = (
                        "Sure — I can add an expense. Please provide:\n"
                        "- amount (e.g., 250)\n- category (e.g., groceries)\n- description (e.g., milk and veggies).\n\n"
                        "Example: 250 for groceries — milk and veggies"
                    )
                    yield msg
                    return
                # Create expense directly
                try:
                    from app.models.finance import Expense
                    exp = Expense(user_id=current_user.id, amount=amt, category=cat, description=desc)
                    db.add(exp)
                    db.commit()
                    db.refresh(exp)
                    yield f"Added expense: {amt:.2f} in '{cat}' — {desc}."
                    return
                except Exception:
                    # Fall back to tool instruction if DB op fails
                    yield (
                        "I couldn't save the expense automatically. You can also use the Tools panel → Add Expense "
                        "and enter amount, category, and description."
                    )
                    return
            if _is_greeting(prompt):
                text = _build_greeting()
            elif ai.is_available and getattr(ai, "llm", None) is not None:
                # Enforce advice template with minimal RAG snippets appended
                final_prompt = (
                    "You are an expert mentor. Use the context if present.\n"
                    "ALWAYS respond in this exact Markdown template with clear, concise content:\n"
                    "## Overview\n"
                    "(1–3 sentences)\n\n"
                    "## Next 3 Steps\n"
                    "- [ ] step\n- [ ] step\n- [ ] step\n\n"
                    "## 3 Resources\n"
                    "1. Title — link\n2. Title — link\n3. Title — link\n\n"
                    "## Risks / Watchouts\n"
                    "- risk\n- risk\n\n"
                    "---\nContext used:\n(List ids/titles or say none)\n\n"
                    f"Context: {context_preamble or 'N/A'}\n"
                    f"Retrieved snippets (top 3): {rag_snippets}\n"
                    f"User: {prompt}\n"
                    "Return only the Markdown body."
                )
                try:
                    text = str(await asyncio.wait_for(_call_llm(ai, final_prompt), timeout=20))
                except Exception:
                    # Timeout or LLM failure — fallback structured template
                    text = _template_wrap("Here’s a focused plan based on your request.", rag_snippets)
            else:
                # Fallback greeting improvement
                text = _build_greeting() if _is_greeting(prompt) else _template_wrap("Here’s a focused plan based on your request.", rag_snippets)
        except Exception:
            text = _build_greeting() if _is_greeting(prompt) else _template_wrap("Here’s a focused plan based on your request.", rag_snippets)

        # naive chunker
        chunk = ""
        for ch in text:
            chunk += ch
            if len(chunk) >= 12:
                yield chunk
                chunk = ""
        if chunk:
            yield chunk

    return StreamingResponse(event_gen(), media_type="text/plain")