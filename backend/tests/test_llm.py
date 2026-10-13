import asyncio
import json
from datetime import date, timedelta

import httpx
import pytest

from app import ai_service
from app.ai_service import analyze_text_to_tasks_with_source, validate_llm_output
from app.config import settings

TOMORROW = (date.today() + timedelta(days=1)).isoformat()


def _groq_body(content: str) -> dict:
    return {"choices": [{"message": {"content": content}}]}


def _gemini_body(content: str) -> dict:
    return {"candidates": [{"content": {"parts": [{"text": content}]}}]}


def _client(handler):
    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


@pytest.fixture
def groq(monkeypatch):
    monkeypatch.setattr(settings, "LLM_PROVIDER", "groq")
    monkeypatch.setattr(settings, "GROQ_API_KEY", "test-key")


@pytest.fixture
def gemini(monkeypatch):
    monkeypatch.setattr(settings, "LLM_PROVIDER", "gemini")
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "test-key")


VALID = json.dumps(
    {"tasks": [{"task": "Pay rent", "category": "Finance", "priority": "High", "deadline": TOMORROW}]}
)


def test_validate_accepts_valid_output():
    tasks = validate_llm_output(VALID)
    assert tasks[0].task == "Pay rent"
    assert tasks[0].deadline.isoformat() == TOMORROW


def test_validate_accepts_bare_array():
    assert len(validate_llm_output(json.dumps(json.loads(VALID)["tasks"]))) == 1


@pytest.mark.parametrize(
    "payload",
    [
        "not json",
        json.dumps({"tasks": []}),
        json.dumps({"tasks": [{"task": "x", "category": "Chores", "priority": "High", "deadline": None}]}),
        json.dumps({"tasks": [{"task": "x", "category": "Work", "priority": "urgent", "deadline": None}]}),
        json.dumps({"tasks": [{"task": "x", "category": "Work", "priority": "High", "deadline": "next friday"}]}),
        json.dumps({"tasks": [{"task": "x", "category": "Work", "priority": "High", "deadline": "2026-02-30"}]}),
        json.dumps({"tasks": [{"task": "x", "category": "Work", "priority": "High", "deadline": "1999-01-01"}]}),
        json.dumps({"tasks": [{"task": "   ", "category": "Work", "priority": "High", "deadline": None}]}),
        json.dumps({"tasks": [{"task": "x", "category": "Work", "priority": "High", "deadline": None, "extra": 1}]}),
    ],
)
def test_validate_rejects_bad_output(payload):
    with pytest.raises(ValueError):
        validate_llm_output(payload)


def test_groq_success(groq):
    seen = {}

    def handler(request: httpx.Request):
        seen["url"] = str(request.url)
        seen["auth"] = request.headers["authorization"]
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json=_groq_body(VALID))

    tasks, source = asyncio.run(analyze_text_to_tasks_with_source("pay rent tomorrow", _client(handler)))
    assert source == "groq"
    assert tasks[0].category == "Finance"
    assert seen["url"] == ai_service.GROQ_URL
    assert seen["auth"] == "Bearer test-key"
    assert seen["body"]["response_format"] == {"type": "json_object"}


def test_gemini_success(gemini):
    def handler(request: httpx.Request):
        assert request.headers["x-goog-api-key"] == "test-key"
        body = json.loads(request.content)
        assert body["generationConfig"]["responseMimeType"] == "application/json"
        return httpx.Response(200, json=_gemini_body(VALID))

    tasks, source = asyncio.run(analyze_text_to_tasks_with_source("pay rent tomorrow", _client(handler)))
    assert source == "gemini"
    assert len(tasks) == 1


@pytest.mark.parametrize(
    "response",
    [
        httpx.Response(500, text="boom"),
        httpx.Response(429, json={"error": "rate limited"}),
        httpx.Response(200, json=_groq_body("Sure! Here are your tasks...")),
        httpx.Response(200, json={"unexpected": True}),
    ],
)
def test_groq_failure_falls_back_to_rules(groq, response):
    tasks, source = asyncio.run(
        analyze_text_to_tasks_with_source("pay rent tomorrow", _client(lambda r: response))
    )
    assert source == "rules"
    assert tasks[0].category == "Finance"


def test_network_error_falls_back(groq):
    def handler(request):
        raise httpx.ConnectError("down")

    _, source = asyncio.run(analyze_text_to_tasks_with_source("call mom", _client(handler)))
    assert source == "rules"


def test_missing_key_uses_rules_without_network(monkeypatch):
    monkeypatch.setattr(settings, "LLM_PROVIDER", "auto")
    monkeypatch.setattr(settings, "GROQ_API_KEY", "")
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "")

    def handler(request):  # pragma: no cover - must not be called
        raise AssertionError("network should not be used")

    _, source = asyncio.run(analyze_text_to_tasks_with_source("call mom", _client(handler)))
    assert source == "rules"


def test_auto_prefers_groq(monkeypatch):
    monkeypatch.setattr(settings, "LLM_PROVIDER", "auto")
    monkeypatch.setattr(settings, "GROQ_API_KEY", "g")
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "m")
    assert settings.resolved_provider() == "groq"
    monkeypatch.setattr(settings, "GROQ_API_KEY", "")
    assert settings.resolved_provider() == "gemini"
