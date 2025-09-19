"""Mock endpoint router for development.

This file programmatically registers mock handlers for the frontend-declared
endpoints that don't yet exist in the backend. Each registered path will
respond to common HTTP methods with a small JSON payload that matches the
domain expectations so the frontend can render pages and run flows.

Note: these mocks are intentionally simple. Replace them with real
implementations as features are developed.
"""
from typing import Any, Callable, Dict, List
from fastapi import APIRouter, Request

router = APIRouter()


# A canonical list of frontend-declared paths that were missing from the
# backend at the time of the comparison. Keep these in sync with the
# output of `tools/compare_endpoints.py` if you regenerate that report.
MISSING_PATHS: List[str] = [
    # ai
    "/ai/analytics",
    "/ai/career",
    "/ai/conversation",
    "/ai/finance",
    "/ai/habits",
    "/ai/insights",
    "/ai/learning",
    "/ai/models",
    "/ai/mood",
    "/ai/personalized",
    "/ai/preferences",
    "/ai/quality",
    "/ai/status",
    "/ai/test",
    "/ai/validation",
    "/ai/wellness",

    # auth extras
    "/auth/preferences",
    "/auth/verify-email",

    # career
    "/career/advice",
    "/career/analytics",
    "/career/assessment",
    "/career/connections",
    "/career/dashboard",
    "/career/events",
    "/career/goals",
    "/career/learning-paths",
    "/career/plan",
    "/career/recommendations",
    "/career/resources",
    "/career/skills",

    # finance
    "/finance/advice",
    "/finance/analytics",
    "/finance/budgets",
    "/finance/categories",
    "/finance/dashboard",
    "/finance/debts",
    "/finance/expenses",
    "/finance/goals",
    "/finance/income",
    "/finance/investments",
    "/finance/plan",
    "/finance/recommendations",
    "/finance/recurring",
    "/finance/reports",

    # gamification
    "/gamification/achievements",
    "/gamification/analytics",
    "/gamification/badges",
    "/gamification/challenges",
    "/gamification/dashboard",
    "/gamification/leaderboards",
    "/gamification/levels",
    "/gamification/milestones",
    "/gamification/quests",
    "/gamification/rewards",
    "/gamification/stats",
    "/gamification/streaks",
    "/gamification/xp",

    # habits
    "/habits/analytics",
    "/habits/categories",
    "/habits/challenges",
    "/habits/dashboard",
    "/habits/events",
    "/habits/reminders",
    "/habits/shared",
    "/habits/tasks",
    "/habits/templates",
    "/habits/today",
    "/habits/upcoming",

    # memory
    "/memory",
    "/memory/analytics",
    "/memory/categories",
    "/memory/cleanup",
    "/memory/context",
    "/memory/conversations",
    "/memory/embeddings",
    "/memory/export",
    "/memory/import",
    "/memory/insights",
    "/memory/preferences",
    "/memory/search",
    "/memory/status",
    "/memory/suggestions",
    "/memory/tags",
    "/memory/trends",

    # mood
    "/mood/ai-insights",
    "/mood/analytics",
    "/mood/current",
    "/mood/dashboard",
    "/mood/exercise",
    "/mood/goals",
    "/mood/journal",
    "/mood/logs",
    "/mood/sleep",
    "/mood/stress",
    "/mood/tips",
    "/mood/trend",
    "/mood/triggers",
    "/mood/wellness",
]


def sample_for_path(path: str) -> Dict[str, Any]:
    """Return a sensible sample payload for the given path prefix."""
    if path.startswith("/ai"):
        return {"status": "ok", "note": "AI mock response"}
    if path.startswith("/career"):
        return {"summary": {"applied": 0, "interviews": 0}, "recommendations": []}
    if path.startswith("/finance"):
        return {"summary": {"balance": 0.0, "expenses_month": 0.0}, "reports": []}
    if path.startswith("/gamification"):
        return {"points": 0, "level": 0, "badges": []}
    if path.startswith("/habits"):
        return {"items": [], "meta": {"count": 0}}
    if path.startswith("/memory"):
        return {"items": [], "status": "idle"}
    if path.startswith("/mood"):
        return {"entries": [], "summary": {}}
    if path.startswith("/auth"):
        return {"message": "ok"}
    return {"message": "mock", "path": path}


def make_handler(path: str) -> Callable:
    async def handler(request: Request):
        return {"mocked": True, "path": path, "method": request.method, "sample": sample_for_path(path)}

    return handler


# Register all missing paths to accept common HTTP methods and return mock data.
COMMON_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]
for p in MISSING_PATHS:
    # add_api_route expects a path without a duplicate prefix; these paths already
    # start with '/'. We intentionally include all common methods so the
    # frontend doesn't get 405 for method mismatch during development.
    router.add_api_route(p, make_handler(p), methods=COMMON_METHODS, include_in_schema=False)

# Keep a few explicit, more detailed mocks (these will override programmatic ones
# because they're registered earlier if included in main.py before the programmatic block).
@router.post("/auth/login")
async def explicit_login(payload: Dict[str, Any]):
    return {"access_token": "dev-token-abc123", "token_type": "bearer", "expires_in": 3600}

@router.post("/auth/register")
async def explicit_register(payload: Dict[str, Any]):
    return {"id": "user_dev_1", "email": payload.get("email"), "message": "registered"}

@router.get("/auth/me")
async def explicit_me():
    return {"id": "user_dev_1", "email": "dev@example.com", "name": "Dev User", "roles": ["user"]}

@router.get("/memory/export")
async def explicit_memory_export():
    return {"file_id": "export_dev_1", "download_url": "/internal/downloads/export_dev_1.json"}
