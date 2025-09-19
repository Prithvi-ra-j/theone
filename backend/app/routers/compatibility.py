"""Compatibility / development stub router.

This router provides lightweight placeholder responses for frontend-declared
endpoints that are not yet implemented in the backend. It's mounted under
the same API prefix (e.g. /api/v1) and is included after all real routers
so it only handles requests that would otherwise return 404.

The goal is to stop noisy 404s during frontend development and give clear
feedback to the client about missing endpoints. Responses use HTTP 501
(Not Implemented) and include a helpful message with the original path.
"""
from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from app.core.config import settings

router = APIRouter()


@router.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"])  # type: ignore[arg-type]
async def compatibility_stub(request: Request, full_path: str):
    """Catch-all stub that returns 501 Not Implemented for missing endpoints.

    This handler is intentionally generic and will only run when no other
    route matches. It returns a JSON object describing the method and path
    that the frontend attempted to call, and a suggestion for next steps.
    """
    method = request.method

    # Helpful response for developers
    payload = {
        "detail": "endpoint_not_implemented",
        "message": (
            f"The endpoint '{settings.API_V1_STR}/{full_path}' (method={method}) "
            "is not implemented on the backend.\n"
            "If this is expected, update the frontend to match the backend API.\n"
            "Otherwise, add a router/handler for this path on the backend."
        ),
        "path": f"{settings.API_V1_STR}/{full_path}",
        "method": method,
        "hint": "Create the missing route or remove/rename the frontend API call.",
    }

    # Use 501 Not Implemented to indicate a missing implementation.
    return JSONResponse(status_code=status.HTTP_501_NOT_IMPLEMENTED, content=payload)
