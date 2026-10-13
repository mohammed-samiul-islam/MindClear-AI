"""Brain-dump -> tasks. Tries a free-tier LLM (Groq or Gemini) with JSON output,
validates the result strictly, and falls back to the rule-based parser on any
failure (missing key, network error, bad JSON, schema violation)."""
from __future__ import annotations

import json
import logging
from datetime import date, timedelta
from typing import List, Literal, Optional, Tuple

import httpx
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from .config import settings
from .rule_parser import rule_based_parse
from .schemas import TaskCreate

logger = logging.getLogger(__name__)

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

SYSTEM_PROMPT = (
    "You convert messy human thoughts into structured tasks.\n"
    "Respond with ONLY a JSON object of the form {{\"tasks\": [...]}}.\n"
    "Each task object has exactly these keys:\n"
    "- \"task\": short actionable description (string)\n"
    "- \"category\": one of \"Work\", \"Personal\", \"Health\", \"Finance\", \"Other\"\n"
    "- \"priority\": one of \"High\", \"Medium\", \"Low\"\n"
    "- \"deadline\": ISO date \"YYYY-MM-DD\" or null. Today is {today} ({weekday}); "
    "resolve relative dates like 'tomorrow' or 'next friday' against it.\n"
)


class LLMTask(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task: str = Field(..., min_length=1, max_length=500)
    category: Literal["Work", "Personal", "Health", "Finance", "Other"]
    priority: Literal["High", "Medium", "Low"]
    deadline: Optional[date] = None

    @field_validator("task")
    @classmethod
    def _strip(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("task must not be blank")
        return v

    @field_validator("deadline", mode="before")
    @classmethod
    def _iso_only(cls, v):
        if v is None or v == "":
            return None
        if not isinstance(v, str):
            raise ValueError("deadline must be an ISO date string or null")
        try:
            return date.fromisoformat(v)
        except ValueError as e:
            raise ValueError(f"deadline is not a valid ISO date: {v!r}") from e

    @field_validator("deadline")
    @classmethod
    def _plausible(cls, v: Optional[date]) -> Optional[date]:
        if v is None:
            return v
        today = date.today()
        if v < today - timedelta(days=366) or v > today + timedelta(days=5 * 366):
            raise ValueError("deadline is implausibly far from today")
        return v


class LLMResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tasks: List[LLMTask] = Field(..., min_length=1, max_length=50)


def validate_llm_output(text: str) -> List[TaskCreate]:
    """Parse and strictly validate raw model text. Raises ValueError on any problem."""
    try:
        data = json.loads(text)
    except (json.JSONDecodeError, TypeError) as e:
        raise ValueError(f"LLM output is not valid JSON: {e}") from e
    if isinstance(data, list):  # tolerate a bare array
        data = {"tasks": data}
    try:
        parsed = LLMResponse.model_validate(data)
    except ValidationError as e:
        raise ValueError(f"LLM output failed validation: {e}") from e
    return [TaskCreate(**t.model_dump()) for t in parsed.tasks]


def _prompt(today: date) -> str:
    return SYSTEM_PROMPT.format(today=today.isoformat(), weekday=today.strftime("%A"))


async def call_groq(raw_text: str, client: httpx.AsyncClient, today: date) -> str:
    resp = await client.post(
        GROQ_URL,
        headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}"},
        json={
            "model": settings.GROQ_MODEL,
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": _prompt(today)},
                {"role": "user", "content": raw_text},
            ],
        },
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


async def call_gemini(raw_text: str, client: httpx.AsyncClient, today: date) -> str:
    resp = await client.post(
        GEMINI_URL.format(model=settings.GEMINI_MODEL),
        headers={"x-goog-api-key": settings.GEMINI_API_KEY},
        json={
            "systemInstruction": {"parts": [{"text": _prompt(today)}]},
            "contents": [{"role": "user", "parts": [{"text": raw_text}]}],
            "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"},
        },
    )
    resp.raise_for_status()
    return resp.json()["candidates"][0]["content"]["parts"][0]["text"]


PROVIDERS = {"groq": call_groq, "gemini": call_gemini}


async def analyze_text_to_tasks_with_source(
    raw_text: str, client: Optional[httpx.AsyncClient] = None
) -> Tuple[List[TaskCreate], str]:
    """Return (tasks, source) where source is "groq", "gemini" or "rules"."""
    today = date.today()
    provider = settings.resolved_provider()
    if provider in PROVIDERS:
        own_client = client is None
        client = client or httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SECONDS)
        try:
            text = await PROVIDERS[provider](raw_text, client, today)
            return validate_llm_output(text), provider
        except Exception as e:  # noqa: BLE001 - any failure -> deterministic fallback
            logger.warning("LLM provider %s failed, using rule-based fallback: %s", provider, e)
        finally:
            if own_client:
                await client.aclose()
    return rule_based_parse(raw_text, today), "rules"


async def analyze_text_to_tasks(raw_text: str) -> List[TaskCreate]:
    tasks, _ = await analyze_text_to_tasks_with_source(raw_text)
    return tasks
