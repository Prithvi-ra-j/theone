"""Opportunities router: internship/hackathon feed (seeded JSON)."""
from typing import Any, List, Optional

from fastapi import APIRouter, Query

router = APIRouter()

# Minimal seeded data (can be moved to a JSON file or DB later)
_OPPORTUNITIES = [
    {
        "id": "int-1",
        "title": "Software Engineering Intern",
        "org": "Startup XYZ",
        "location": "Bengaluru, IN",
        "remote": True,
        "link": "https://example.com/opportunity/se-intern",
        "tags": ["internship", "software", "javascript"],
    },
    {
        "id": "hack-1",
        "title": "National Hackathon 2025",
        "org": "GovTech India",
        "location": "Hybrid",
        "remote": True,
        "link": "https://example.com/opportunity/national-hackathon",
        "tags": ["hackathon", "ai", "civictech"],
    },
    {
        "id": "int-2",
        "title": "Data Analyst Intern",
        "org": "Analytics Co",
        "location": "Pune, IN",
        "remote": False,
        "link": "https://example.com/opportunity/da-intern",
        "tags": ["internship", "data", "sql"],
    },
]


@router.get("/opportunities", response_model=List[dict])
async def list_opportunities(
    q: Optional[str] = Query(None, description="Search text (title/org/tags)"),
    remote: Optional[bool] = Query(None),
    limit: int = Query(20, ge=1, le=100),
) -> Any:
    """Return a simple feed of internships/hackathons with basic filters."""
    items = _OPPORTUNITIES
    # Text query on title/org/tags
    if q:
        ql = q.lower()
        items = [
            it for it in items
            if ql in it.get("title", "").lower()
            or ql in it.get("org", "").lower()
            or any(ql in t.lower() for t in it.get("tags", []))
        ]
    # Remote filter
    if remote is not None:
        items = [it for it in items if bool(it.get("remote")) == bool(remote)]

    return items[:limit]
