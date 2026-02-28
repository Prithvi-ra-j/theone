import asyncio
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.routers.auth import get_optional_current_user
from fastapi import APIRouter, HTTPException, status, Depends
from typing import Any, Dict, List, Optional
from app.models.user import User

from app.core.config import settings

router = APIRouter()

@router.get("/status")
async def ai_status():
    """Return AI provider availability and model details for UI health badges.

    Response example:
    {"available": true, "provider": "ollama|api|gemini", "model": "llama3|gpt-4o-mini|..."}
    """
    try:
        from app.main import ai_service  # type: ignore
    except Exception:
        ai_service = None

    if ai_service is None:
        return {"available": False, "provider": None, "model": None}

    try:
        from app.core.config import settings
        provider = getattr(settings, "LLM_PROVIDER", None)
    except Exception:
        provider = None

    return {
        "available": bool(getattr(ai_service, "is_available", False)),
        "provider": provider,
        "model": getattr(ai_service, "model_name", None),
    }


@router.post("/conversation")
async def conversation(
    payload: Dict[str, Any],
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """Proxy conversation requests to the AI service with context awareness.

    Expects payload: { "messages": [ ... ], "language": "english" }
    """
    messages: List[Dict[str, str]] = payload.get("messages")
    language: str = payload.get("language", "english")
    
    if not messages:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="messages required")

    # Use the application's shared AI service created during lifespan.
    try:
        from app.main import ai_service  # type: ignore
    except Exception:
        ai_service = None

    if ai_service is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AI service not configured")

    # Inject language instruction into the first system message or add one
    lang_instr = ai_service._get_language_instruction(language)
    has_system = False
    for msg in messages:
        if msg.get("role") == "system":
            msg["content"] = f"{msg.get('content', '')}\n\nLanguage Instruction: {lang_instr}"
            has_system = True
            break
    
    if not has_system:
        messages.insert(0, {"role": "system", "content": f"Language Instruction: {lang_instr}"})

    # Run the provider call with a short timeout
    timeout_seconds = 20
    user_id = current_user.id if current_user else None
    try:
        result = await asyncio.wait_for(
            ai_service.conversation(messages, language=language, user_id=user_id, db=db), 
            timeout=timeout_seconds
        )
        return result
    except asyncio.TimeoutError:
        return {"status": "accepted", "detail": "Request is being processed (timeout reached)"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except asyncio.TimeoutError:
        return {"status": "accepted", "detail": "Request is being processed (timeout reached)"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
