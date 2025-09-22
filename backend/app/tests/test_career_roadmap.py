
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from fastapi import HTTPException

# Import the CareerService directly
from app.services.career_service import CareerService


class DummyUser:
    id = 1
    email = "demo@example.com"


class FakeQuery:
    def __init__(self, results=None):
        self._results = results or []

    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def all(self):
        return self._results

    def first(self):
        return self._results[0] if self._results else None


class FakeDB:
    def __init__(self, goals=None, skills=None):
        self._goals = goals or []
        self._skills = skills or []

    def query(self, model):
        if 'CareerGoal' in getattr(model, '__name__', ''):
            return FakeQuery(self._goals)
        if 'Skill' in getattr(model, '__name__', ''):
            return FakeQuery(self._skills)
        return FakeQuery()


@pytest.mark.asyncio
async def test_generate_roadmap_happy_path(monkeypatch, tmp_path):
    # Arrange: create a CareerService instance with mocked ai_service and memory_service
    fake_db = FakeDB()
    service = CareerService(db=fake_db)

    # Mock ai_service.career_advisor to return a clean JSON string in the dict shape used by service
    sample_response = {"advice": json.dumps([
        {
            "title": "Milestone 1",
            "description": "Start learning",
            "estimated_weeks": 4,
            "tasks": [
                {"title": "Read book", "description": "Read intro", "est_hours": 5}
            ]
        }
    ])}

    mock_ai = MagicMock()
    mock_ai.career_advisor = AsyncMock(return_value=sample_response)

    # MemoryService should be called but can return empty context
    mock_memory = MagicMock()
    mock_memory.get_user_context = AsyncMock(return_value={})

    # Patch service attributes
    service.ai_service = mock_ai
    service.memory_service = mock_memory

    # Act
    result = await service.generate_roadmap(DummyUser(), payload={})

    # Assert
    assert isinstance(result, list)
    assert len(result) == 1
    m = result[0]
    assert m['title'] == "Milestone 1"
    assert isinstance(m['tasks'], list)


@pytest.mark.asyncio
async def test_generate_roadmap_fallback_when_ai_unavailable(monkeypatch):
    fake_db = FakeDB()
    service = CareerService(db=fake_db)

    # ai_service unavailable -> raise or return falsy
    mock_ai = MagicMock()
    mock_ai.career_advisor = AsyncMock(side_effect=Exception("LLM down"))

    service.ai_service = mock_ai
    service.memory_service = MagicMock()

    result = await service.generate_roadmap(DummyUser(), payload={})

    # Should return deterministic fallback list
    assert isinstance(result, list)
    assert len(result) >= 1


@pytest.mark.asyncio
async def test_generate_roadmap_parses_code_fence_json(monkeypatch):
    fake_db = FakeDB()
    service = CareerService(db=fake_db)

    # AI returns JSON wrapped in ```json ``` fences inside the advice field
    advice = "Here is the plan:\n```json\n[{\"title\": \"Fence\", \"description\": \"Inside\", \"estimated_weeks\": 2, \"tasks\": []}]\n```"
    mock_ai = MagicMock()
    mock_ai.career_advisor = AsyncMock(return_value={"advice": advice})

    service.ai_service = mock_ai
    service.memory_service = MagicMock()

    result = await service.generate_roadmap(DummyUser(), payload={})
    assert isinstance(result, list)
    assert result[0]["title"] == "Fence"


@pytest.mark.asyncio
async def test_generate_roadmap_uses_memory_context(monkeypatch):
    # Ensure memory content is attached to user_context and ai_service invoked with it
    fake_db = FakeDB()
    service = CareerService(db=fake_db)

    # Memory provides some notes that AI might use
    mem = {"notes": "User has built 2 projects"}
    mock_memory = MagicMock()
    mock_memory.get_user_context = AsyncMock(return_value=mem)

    captured_ctx = {}

    async def fake_career_advisor(user_context, prompt, temperature=0.0, user_id=None):
        # capture user_context for assertion
        captured_ctx.update(user_context)
        return {"advice": json.dumps([{"title": "FromMemory", "description": "Uses memory", "estimated_weeks": 1, "tasks": []}])}

    mock_ai = MagicMock()
    mock_ai.career_advisor = AsyncMock(side_effect=fake_career_advisor)

    service.ai_service = mock_ai
    service.memory_service = mock_memory

    result = await service.generate_roadmap(DummyUser(), payload={})
    assert "memory" in captured_ctx
    assert captured_ctx["memory"] == mem
    # Result should be a list; AI may return a structured roadmap or a fallback string.
    assert isinstance(result, list)
    assert len(result) >= 1


@pytest.mark.asyncio
async def test_generate_roadmap_parses_json_in_code_fence(monkeypatch):
    service = CareerService(db=None)

    # LLM returns JSON wrapped in markdown code fences
    sample_wrapped = """Here is the roadmap:\n```json\n[{"title": "Fence Milestone", "description": "From code fence", "estimated_weeks": 2, "tasks": []}]\n```"""

    mock_ai = MagicMock()
    mock_ai.career_advisor = AsyncMock(return_value=sample_wrapped)

    service.ai_service = mock_ai
    service.memory_service = MagicMock()

    result = await service.generate_roadmap(DummyUser(), payload={})

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["title"] == "Fence Milestone"


@pytest.mark.asyncio
async def test_generate_roadmap_uses_memory_context(monkeypatch):
    service = CareerService(db=None)

    # AI echoes back context hint if provided; ensure memory_service was consulted
    def ai_side_effect(user_context, prompt, **kwargs):
        # confirm the prompt includes a memory snippet marker
        assert "MEMORY_SNIPPET" in prompt or "recent memories" in prompt
        # return a JSON string as many LLM adapters do
        return json.dumps([
            {"title": "From Memory", "description": "Incorporated memory", "estimated_weeks": 1, "tasks": []}
        ])

    mock_ai = MagicMock()
    mock_ai.career_advisor = AsyncMock(side_effect=ai_side_effect)

    # Memory service should return some context items
    mock_memory = MagicMock()
    mock_memory.semantic_search = AsyncMock(return_value=[{"content": "I like backend engineering"}])

    service.ai_service = mock_ai
    service.memory_service = mock_memory

    result = await service.generate_roadmap(DummyUser(), payload={})

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["title"] == "From Memory"
