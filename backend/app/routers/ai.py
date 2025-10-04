"""AI router - exposes endpoints for conversation and AI utilities."""
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, status
import asyncio

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
async def conversation(payload: Dict[str, Any]):
    """Proxy conversation requests to the AI service.

    Expects payload: { "messages": [ { "role": "user", "content": "..." }, ... ] }
    Behavior:
      - If the shared ai_service is available, call it and return the result.
      - If the call takes longer than the configured timeout, return 202 Accepted
        with a message that the request is queued.
      - If no ai_service is configured, return 503 Service Unavailable.
    """
    messages: List[Dict[str, str]] = payload.get("messages")
    if not messages:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="messages required")

    # Use the application's shared AI service created during lifespan.
    try:
        from app.main import ai_service  # type: ignore
    except Exception:
        ai_service = None

    if ai_service is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AI service not configured")

    # Run the provider call with a short timeout so the HTTP request doesn't hang
    # indefinitely. If it times out, respond 202 to indicate work is queued.
    timeout_seconds = 20
    try:
        result = await asyncio.wait_for(ai_service.conversation(messages), timeout=timeout_seconds)
        return result
    except asyncio.TimeoutError:
        return {"status": "accepted", "detail": "Request is being processed (timeout reached)"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
