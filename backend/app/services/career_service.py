"""CareerService: business logic for career roadmap, tasks and advice."""
from typing import Any, Dict, List, Optional
import json
import re
from loguru import logger

from sqlalchemy.orm import Session
from app.models.user import User


class CareerService:
    def __init__(self, db: Session, ai_service: Optional[Any] = None, memory_service: Optional[Any] = None):
        self.db = db
        # Try to use injected services, otherwise attempt to import shared instances
        if ai_service is None:
            try:
                from app.main import ai_service as _ai  # type: ignore
                ai_service = _ai
            except Exception:
                ai_service = None
        if memory_service is None:
            try:
                from app.main import memory_service as _ms  # type: ignore
                memory_service = _ms
            except Exception:
                memory_service = None

        self.ai_service = ai_service
        self.memory_service = memory_service

    def _parse_json_from_text(self, text: str) -> Optional[Any]:
        if not text:
            return None
        # 1) direct parse
        try:
            return json.loads(text)
        except Exception:
            pass

        # 2) extract JSON block from ```json ... ```
        m = re.search(r"```json\s*(\{[\s\S]*?\}|\[[\s\S]*?\])\s*```", text, re.IGNORECASE)
        if m:
            try:
                return json.loads(m.group(1))
            except Exception:
                pass

        # 3) find first JSON-like substring
        m2 = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)
        if m2:
            try:
                return json.loads(m2.group(1))
            except Exception:
                pass

        return None

    async def generate_roadmap(self, effective_user: Optional[User], payload: Optional[dict] = None) -> List[dict]:
        """Generate a roadmap for the user. Returns list of milestone dicts.

        Payload may include 'focus', 'horizon', and 'education'.
        """
        # Build user_context
        user_context: Dict[str, Any] = {"user_id": effective_user.id if effective_user else None}
        try:
            if effective_user:
                from app.models.career import CareerGoal, Skill  # local import
                goals = self.db.query(CareerGoal).filter(CareerGoal.user_id == effective_user.id).all()
                skills = self.db.query(Skill).filter(Skill.user_id == effective_user.id).all()
                user_context["goals"] = [{"id": g.id, "title": g.title, "description": getattr(g, 'description', None), "status": g.status} for g in goals]
                user_context["skills"] = [{"id": s.id, "name": s.name, "current_level": getattr(s, 'current_level', None), "target_level": getattr(s, 'target_level', None)} for s in skills]
            else:
                user_context["goals"] = []
                user_context["skills"] = []
        except Exception as e:
            logger.debug("Error building DB context for roadmap: %s", e)
            user_context["goals"] = []
            user_context["skills"] = []

        # Merge memory context
        if self.memory_service and effective_user:
            try:
                mem = None
                if hasattr(self.memory_service, "get_user_context"):
                    maybe = self.memory_service.get_user_context(effective_user.id, context_type="career")
                    if hasattr(maybe, "__await__"):
                        mem = await maybe
                    else:
                        mem = maybe
                if not isinstance(mem, (dict, list, str)) and hasattr(self.memory_service, "semantic_search"):
                    maybe2 = self.memory_service.semantic_search(user_id=effective_user.id, query="career", top_k=10)
                    if hasattr(maybe2, "__await__"):
                        mem = await maybe2
                    else:
                        mem = maybe2
                if not isinstance(mem, (dict, list, str)):
                    mem = None
                user_context["memory"] = mem or {}
            except Exception as e:
                logger.debug("Memory service error when building roadmap context: %s", e)
                user_context["memory"] = {}
        else:
            user_context["memory"] = {}

        # Options controlling the roadmap
        opts = payload or {}
        focus = opts.get("focus") or "career"
        horizon = opts.get("horizon") or "12 weeks"
        edu = opts.get("education") or {}
        edu_level = edu.get("level")
        edu_start = edu.get("start_date")
        edu_end = edu.get("end_date")

        # Strict JSON-only prompt
        prompt = (
            "You are Dristhi, an AI career advisor. Using the provided user context, RETURN ONLY a valid JSON array (no explanation, no markdown). "
            "Each array item must be an object with keys: title (string), description (string), estimated_weeks (integer or string), tasks (array of objects with title, description, est_hours). "
            "Use culturally relevant, practical milestones and realistic time estimates for Indian students. "
            f"Focus: {focus}. Time horizon: {horizon}. "
            f"Education: level={edu_level}, start={edu_start}, end={edu_end}. If level suggests final-year, emphasize interview prep, system design, and 2-3 portfolio projects. If early-year, emphasize fundamentals, breadth, and emerging topics.\n\n"
            "Example:\n[{\n  \"title\": \"Build fundamental skills\",\n  \"description\": \"Gain hands-on experience with projects and core concepts.\",\n  \"estimated_weeks\": 8,\n  \"tasks\": [{\"title\": \"Complete project A\", \"description\": \"Build a small web app\", \"est_hours\": 20}]\n}]\n"
        )

        # Append recent memory snippet if available
        try:
            mem = user_context.get("memory")
            mem_text = None
            if mem:
                if isinstance(mem, dict):
                    mem_text = str(mem.get("content")) if mem.get("content") is not None else json.dumps(mem)
                elif isinstance(mem, list):
                    parts = []
                    for item in mem:
                        if isinstance(item, dict):
                            parts.append(item.get("content") or item.get("text") or json.dumps(item))
                        else:
                            parts.append(str(item))
                    mem_text = "\n".join(parts)
            if mem_text:
                prompt += f"\n\nRecent memories (for context):\nMEMORY_SNIPPET:\n{mem_text}\n"
        except Exception:
            pass

        # Fallback if AI unavailable
        if self.ai_service is None:
            try:
                if effective_user:
                    from app.models.career import CareerGoal
                    active = self.db.query(CareerGoal).filter(CareerGoal.user_id == effective_user.id, CareerGoal.status == 'active').order_by(CareerGoal.created_at.desc()).first()
                else:
                    active = None
            except Exception:
                active = None

            if active:
                return [{
                    "title": f"Prepare for {active.title}",
                    "description": getattr(active, 'description', '') or "Work towards the active goal",
                    "estimated_weeks": 12,
                    "tasks": [
                        {"title": "Define milestones", "description": "Break goal into smaller milestones", "est_hours": 5},
                        {"title": "Build project", "description": "Create a small project demonstrating relevant skills", "est_hours": 40},
                    ]
                }]

            return [{
                "title": "Set clear career goal",
                "description": "Define a specific role or outcome to aim for.",
                "estimated_weeks": 4,
                "tasks": [{"title": "Write down goal", "description": "Write a clear goal statement", "est_hours": 1}]
            }]

        # AI path
        try:
            ai_result = await self.ai_service.career_advisor(user_context, prompt, temperature=0.0, user_id=(effective_user.id if effective_user else None))
            advice_text = None
            if isinstance(ai_result, dict):
                advice_text = ai_result.get("advice") or next((v for v in ai_result.values() if isinstance(v, str)), None)
            elif isinstance(ai_result, str):
                advice_text = ai_result

            parsed = self._parse_json_from_text(advice_text) if advice_text else None
            if isinstance(parsed, list):
                return parsed
            if advice_text:
                return [{"title": "AI Roadmap", "description": advice_text, "estimated_weeks": "unknown", "tasks": []}]
            return [{"title": "Plan your career", "description": "AI returned no structured roadmap; try again later.", "estimated_weeks": "unknown", "tasks": []}]
        except Exception as e:
            logger.exception("Error in CareerService.generate_roadmap: %s", e)
            return [{"title": "Plan your career (fallback)", "description": str(e), "estimated_weeks": "unknown", "tasks": []}]
