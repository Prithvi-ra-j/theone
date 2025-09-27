import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import SessionLocal
from app.models.user import User
from app.models.career import CareerGoal
from app.services.career_service import CareerService


@pytest.mark.integration
def test_generate_roadmap_flow(monkeypatch):
    """
    Integration smoke test for the career vertical slice.

    Steps:
    - Ensure DB is reachable and migrations have been applied.
    - Create (or find) a demo user directly in the DB.
    - Create a CareerGoal row for that demo user.
    - Call the generate-roadmap endpoint (unauthenticated). Router resolves the demo user.
    - Assert the response is a list of RoadmapMilestone-like objects.
    """

    # Provide a fixed sample roadmap so the test is deterministic and doesn't call external LLMs.
    sample_roadmap = [
        {
            "title": "Milestone 1 - Fundamentals",
            "description": "Learn basics",
            "estimated_weeks": 2,
            "tasks": [
                {"title": "Read intro", "description": "Read the basics", "estimated_hours": 2},
                {"title": "Practice exercises", "description": "Do small exercises", "estimated_hours": 4},
            ],
        },
        {
            "title": "Milestone 2 - Build project",
            "description": "Apply knowledge",
            "estimated_weeks": 4,
            "tasks": [
                {"title": "Design project", "description": "Sketch the app", "estimated_hours": 3},
                {"title": "Implement MVP", "description": "Code core features", "estimated_hours": 12},
            ],
        },
    ]

    # Patch CareerService.generate_roadmap to return the sample roadmap.
    # Use an async stub because the real implementation may be async.
    async def _fake_generate_roadmap(self, effective_user, payload):
        return sample_roadmap

    monkeypatch.setattr(CareerService, "generate_roadmap", _fake_generate_roadmap, raising=True)

    # Arrange: insert demo user + career goal directly into DB
    db = SessionLocal()
    try:
        demo = db.query(User).filter(User.email == "demo@example.com").first()
        if not demo:
            demo = User(email="demo@example.com", hashed_password="dev", full_name="Demo User")
            db.add(demo)
            db.commit()
            db.refresh(demo)

        goal = CareerGoal(
            title="Integration Test Goal",
            description="Short description for integration test",
            user_id=demo.id
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)
    finally:
        db.close()

    client = TestClient(app)

    # Act: call the roadmap endpoint (unauthenticated). Router should pick demo user.
    resp = client.post("/api/v1/career/generate-roadmap", json={"goal_title": goal.title})

    # Assert: basic structural checks
    assert resp.status_code == 200, f"expected 200 OK, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert isinstance(body, list), "expected a list of milestones"
    # Basic schema expectations: each milestone has title and tasks
    assert len(body) > 0, "expected at least one milestone"
    for m in body:
        assert "title" in m and isinstance(m["title"], str)
        assert "tasks" in m and isinstance(m["tasks"], list)