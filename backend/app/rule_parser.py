"""Rule-based fallback: split a brain dump into tasks and classify each one
by keyword matching. Deterministic, offline and free."""
from __future__ import annotations

import re
from datetime import date
from typing import List, Optional

from .date_parser import parse_deadline
from .schemas import TaskCreate

CATEGORY_KEYWORDS = {
    "Work": [
        "meeting", "email", "boss", "client", "project", "deadline", "report",
        "presentation", "slides", "deploy", "code", "bug", "review", "pr",
        "standup", "manager", "team", "office", "interview", "resume", "cv",
        "proposal", "invoice client", "sprint", "ticket", "colleague", "work",
        "job", "apply", "linkedin", "portfolio",
    ],
    "Health": [
        "doctor", "dentist", "gym", "workout", "exercise", "run", "running",
        "yoga", "meditate", "therapy", "therapist", "medicine", "meds",
        "pharmacy", "prescription", "sleep", "diet", "walk", "hospital",
        "checkup", "appointment", "vitamins", "water", "health",
    ],
    "Finance": [
        "pay", "bill", "bills", "rent", "tax", "taxes", "bank", "budget",
        "invoice", "loan", "credit card", "insurance", "mortgage", "salary",
        "refund", "subscription", "transfer", "money", "savings", "invest",
    ],
    "Personal": [
        "mom", "dad", "mum", "family", "friend", "birthday", "call", "groceries",
        "grocery", "clean", "laundry", "cook", "dinner", "gift", "kids", "wife",
        "husband", "partner", "home", "house", "shopping", "buy", "book",
        "read", "movie", "vacation", "trip", "pet", "dog", "cat",
    ],
}
# Tie-break order when two categories score equally.
CATEGORY_ORDER = ["Finance", "Health", "Work", "Personal"]

HIGH_KEYWORDS = [
    "urgent", "asap", "immediately", "important", "critical", "must",
    "overdue", "deadline", "today", "tonight", "now", "emergency", "!!",
]
LOW_KEYWORDS = [
    "maybe", "someday", "eventually", "sometime", "if time", "when possible",
    "low priority", "not urgent", "whenever", "might", "could",
]

_SPLIT_RE = re.compile(
    r"\n+|;|\u2022|(?<=[.!?])\s+(?=[A-Za-z])|,(?!\s*\d{4}\b)|\s+and then\s+|\s+also\s+",
)
_BULLET_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s*")
_FILLER_RE = re.compile(r"^(?:i\s+(?:need|have|want|should)\s+to|need\s+to|have\s+to|gotta|must|remember\s+to|don'?t\s+forget\s+to)\s+", re.I)


def _contains(text: str, keyword: str) -> bool:
    if not keyword.isalnum() and " " not in keyword:
        return keyword in text
    return re.search(rf"\b{re.escape(keyword)}\b", text) is not None


def classify_category(text: str) -> str:
    t = text.lower()
    scores = {cat: sum(_contains(t, kw) for kw in kws) for cat, kws in CATEGORY_KEYWORDS.items()}
    best = max(CATEGORY_ORDER, key=lambda c: (scores[c], -CATEGORY_ORDER.index(c)))
    return best if scores[best] > 0 else "Other"


def classify_priority(text: str, deadline: Optional[date] = None, today: Optional[date] = None) -> str:
    t = text.lower()
    if any(_contains(t, kw) for kw in HIGH_KEYWORDS):
        return "High"
    if any(_contains(t, kw) for kw in LOW_KEYWORDS):
        return "Low"
    if deadline is not None:
        days = (deadline - (today or date.today())).days
        if days <= 1:
            return "High"
        if days <= 7:
            return "Medium"
        return "Low"
    return "Medium"


def split_items(raw_text: str) -> List[str]:
    items = []
    for part in _SPLIT_RE.split(raw_text):
        if not part:
            continue
        cleaned = _BULLET_RE.sub("", part).strip(" \t.-")
        cleaned = _FILLER_RE.sub("", cleaned).strip()
        if cleaned:
            items.append(cleaned[0].upper() + cleaned[1:])
    return items


def rule_based_parse(raw_text: str, today: Optional[date] = None) -> List[TaskCreate]:
    today = today or date.today()
    tasks = []
    for item in split_items(raw_text):
        deadline = parse_deadline(item, today)
        tasks.append(
            TaskCreate(
                task=item,
                category=classify_category(item),
                priority=classify_priority(item, deadline, today),
                deadline=deadline,
            )
        )
    if not tasks:
        raise ValueError("No tasks could be parsed from the input.")
    return tasks
