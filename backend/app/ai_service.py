import json
from typing import List

import httpx

from .config import settings
from .schemas import TaskCreate, CategoryType, PriorityType


SYSTEM_PROMPT = (
    "You are an assistant that converts messy human thoughts into structured task objects.\n"
    "Return ONLY a valid JSON array of task objects, with no explanation or extra text.\n"
    "Each task object must have exactly these fields:\n"
    "- task (string)\n"
    "- category (one of: 'Work', 'Personal', 'Health', 'Finance', 'Other')\n"
    "- priority (one of: 'High', 'Medium', 'Low')\n"
    "- deadline (an ISO date string like '2026-03-05' or null)\n"
)


async def call_huggingface(raw_text: str) -> str:
    """
    Call the Hugging Face Inference API and return the raw generated text.
    """
    if not settings.HUGGINGFACE_API_TOKEN:
        raise RuntimeError(
            "HUGGINGFACE_API_TOKEN is not set. Please add it to your .env file."
        )

    url = f"https://api-inference.huggingface.co/models/{settings.HUGGINGFACE_MODEL}"
    headers = {
        "Authorization": f"Bearer {settings.HUGGINGFACE_API_TOKEN}",
        "Accept": "application/json",
    }

    # We wrap the system instructions and user text in a single prompt.
    prompt = f"{SYSTEM_PROMPT}\n\nUser text:\n{raw_text}\n\nJSON:"

    # Many text-generation models accept this payload shape.
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 512,
            "temperature": 0.2,
        },
    }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(url, headers=headers, json=payload)

    response.raise_for_status()
    data = response.json()

    # The common serverless format is a list with generated_text.
    if isinstance(data, list) and data and "generated_text" in data[0]:
        return data[0]["generated_text"]

    # Fallback: if it's already plain text or different, stringify it.
    if isinstance(data, str):
        return data
    return json.dumps(data)


def _extract_json_array(text: str) -> list:
    """
    Try to parse a JSON array from the model's output.
    We first try to load the whole text; if that fails, we look for the first
    '[' and last ']' and try to parse that slice.
    """
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        pass

    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1 and end > start:
        snippet = text[start : end + 1]
        parsed = json.loads(snippet)
        if isinstance(parsed, list):
            return parsed

    raise ValueError("Model did not return a valid JSON array.")


def _coerce_category(value: str) -> CategoryType:
    normalized = (value or "").strip().lower()
    mapping = {
        "work": "Work",
        "personal": "Personal",
        "health": "Health",
        "finance": "Finance",
        "other": "Other",
    }
    return mapping.get(normalized, "Other")  # type: ignore[return-value]


def _coerce_priority(value: str) -> PriorityType:
    normalized = (value or "").strip().lower()
    mapping = {
        "high": "High",
        "medium": "Medium",
        "low": "Low",
    }
    return mapping.get(normalized, "Medium")  # type: ignore[return-value]


def _simple_local_parse(raw_text: str) -> List[TaskCreate]:
    """
    Fallback parser that works entirely locally with no external AI.
    It splits the input on commas/newlines and creates medium-priority tasks.
    This keeps the app usable even if the remote model is unavailable.
    """
    # Split on commas and newlines
    raw_items = []
    for part in raw_text.replace("\n", ",").split(","):
        cleaned = part.strip()
        if cleaned:
            raw_items.append(cleaned)

    tasks: List[TaskCreate] = []
    for item in raw_items:
        tasks.append(
            TaskCreate(
                task=item,
                category="Other",
                priority="Medium",
                deadline=None,
            )
        )

    if not tasks:
        raise ValueError("No tasks could be parsed from the input.")

    return tasks


async def analyze_text_to_tasks(raw_text: str) -> List[TaskCreate]:
    """
    High-level helper: optionally call the Hugging Face model, parse JSON, and
    validate into TaskCreate objects. If USE_HUGGINGFACE is false, we fall back
    to a simple local parser so the app works completely free of cost.
    """
    if not settings.USE_HUGGINGFACE:
        # Completely free, offline-friendly behavior.
        return _simple_local_parse(raw_text)

    raw_output = await call_huggingface(raw_text)
    items = _extract_json_array(raw_output)

    tasks: List[TaskCreate] = []
    for item in items:
        if not isinstance(item, dict):
            continue

        task_str = str(item.get("task", "")).strip()
        if not task_str:
            continue

        category = _coerce_category(str(item.get("category", "")))
        priority = _coerce_priority(str(item.get("priority", "")))
        deadline = item.get("deadline", None)

        tasks.append(
            TaskCreate(
                task=task_str,
                category=category,
                priority=priority,
                deadline=deadline,
            )
        )

    if not tasks:
        raise ValueError("No valid tasks were extracted from the model output.")

    return tasks


