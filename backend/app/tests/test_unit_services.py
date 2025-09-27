# backend/app/tests/test_unit_services.py

import json
import pytest

from app.services.ai_service import AIService
from app.services.career_service import CareerService


def test_ai_fallback_response_keys():
    svc = AIService()
    fb = svc._fallback_response("career_advisor")
    assert isinstance(fb, dict)
    assert "advice" in fb
    assert fb.get("model") == "fallback"


def test_ai_generate_tasks_with_callable_llm_parses_json():
    svc = AIService()

    # Provide a callable LLM that returns JSON text
    def fake_llm(prompt: str):
        return json.dumps([{"title": "t1", "description": "d1"}, {"title": "t2", "description": "d2"}])

    svc.llm = fake_llm

    tasks = svc.generate_tasks_for_goal("Goal X", "Some context")
    assert isinstance(tasks, list)
    assert tasks and isinstance(tasks[0], dict)
    assert tasks[0]["title"] == "t1"


def test_ai_generate_tasks_with_callable_llm_nonjson_returns_wrapped():
    svc = AIService()

    def fake_llm_plain(prompt: str):
        return "A plain-text reply not JSON"

    svc.llm = fake_llm_plain

    tasks = svc.generate_tasks_for_goal("Goal X", "Some context")
    assert isinstance(tasks, list)
    # When result is non-JSON, generate_tasks_for_goal wraps it into a list with title/description fallback
    assert isinstance(tasks[0], dict) and "title" in tasks[0]


def test_ai_generate_feedback_callable_llm():
    svc = AIService()

    def fake_llm(prompt: str):
        return "Nice progress — keep building projects."

    svc.llm = fake_llm

    feedback = svc.generate_feedback("Goal X", [{"title": "t1"}])
    assert isinstance(feedback, str)
    assert "Nice progress" in feedback


def test_ai_get_status_shape():
    svc = AIService()
    s = svc.get_status()
    assert isinstance(s, dict)
    assert "available" in s and "provider" in s and "model" in s


def test_career_parse_json_direct_and_fenced():
    # _parse_json_from_text is instance method but independent of DB; pass db=None
    cs = CareerService(db=None)
    # direct JSON
    text = '[{"title": "A", "tasks": []}]'
    parsed = cs._parse_json_from_text(text)
    assert isinstance(parsed, list)
    assert parsed[0]["title"] == "A"

    # fenced JSON
    fenced = "Here is result:\n```json\n{\"title\": \"B\", \"tasks\": []}\n```"
    parsed2 = cs._parse_json_from_text(fenced)
    assert isinstance(parsed2, dict) or isinstance(parsed2, list)
    # If dict, check title; if list, check item
    if isinstance(parsed2, dict):
        assert parsed2.get("title") == "B"
    else:
        assert parsed2[0]["title"] == "B"

    # embedded JSON in text
    embedded = "Some text ... {\"title\": \"C\", \"tasks\": []} ... end"
    parsed3 = cs._parse_json_from_text(embedded)
    assert parsed3 and (parsed3.get("title") == "C" or parsed3[0]["title"] == "C")


@pytest.mark.asyncio
async def test_career_generate_roadmap_fallback_no_ai():
    # CareerService should return a DB-free fallback roadmap if ai_service is None and no active goal.
    cs = CareerService(db=None, ai_service=None, memory_service=None)
    # Call with no effective_user (None) so DB queries are skipped/caught
    roadmap = await cs.generate_roadmap(effective_user=None, payload=None)
    assert isinstance(roadmap, list)
    assert len(roadmap) > 0
    item = roadmap[0]
    assert "title" in item and "tasks" in item