from typing import Any, Dict, List
import os

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.core.config import settings

router = APIRouter()


@router.get("/debug/cors")
async def debug_cors(request: Request) -> JSONResponse:
    """Return information about the incoming Origin and the backend CORS settings.

    This endpoint is intended as a temporary diagnostic aid (safe to leave
    in place but can be removed after debugging). It does not modify CORS
    behavior, it only reports what the backend is configured with and
    whether the incoming Origin would be allowed by the current settings.
    """
    origin = request.headers.get("origin")

    # Normalize configured origins to strings
    configured: List[str] = [str(u) for u in (settings.BACKEND_CORS_ORIGINS or [])]

    # Dynamic echo allowed when DEBUG or ALLOW_CORS_FROM_REQUEST is set
    allow_dynamic = bool(settings.DEBUG) or os.getenv("ALLOW_CORS_FROM_REQUEST", "0") == "1"

    origin_allowed = False
    if origin:
        if origin in configured:
            origin_allowed = True
        elif allow_dynamic:
            origin_allowed = True

    payload: Dict[str, Any] = {
        "origin_received": origin,
        "backend_cors_origins": configured,
        "frontend_url_setting": str(settings.FRONTEND_URL) if getattr(settings, "FRONTEND_URL", None) else None,
        "allow_dynamic": allow_dynamic,
        "origin_allowed": origin_allowed,
        # Helpful note for what client should expect
        "expected_response_header": (
            {"Access-Control-Allow-Origin": origin} if origin_allowed and origin else {}
        ),
    }

    return JSONResponse(status_code=200, content=payload)
