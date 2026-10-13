"""Natural-language deadline parsing (no external dependencies).

Supported phrases (case-insensitive):
  today, tonight, tomorrow/tmrw, day after tomorrow,
  weekdays ("friday", "on fri", "by monday", "next tuesday", "this thursday"),
  "next week" (next Monday), "this weekend"/"weekend" (Saturday),
  "end of week"/"eow" (Friday), "end of month"/"eom",
  "in N days/weeks", ISO dates (2026-03-05), numeric dates (3/5, 3/5/2026),
  month-name dates ("March 5", "Mar 5th, 2026", "5 March").
"""
from __future__ import annotations

import calendar
import re
from datetime import date, timedelta
from typing import Optional

WEEKDAYS = {
    "monday": 0, "mon": 0,
    "tuesday": 1, "tue": 1, "tues": 1,
    "wednesday": 2, "wed": 2,
    "thursday": 3, "thu": 3, "thur": 3, "thurs": 3,
    "friday": 4, "fri": 4,
    "saturday": 5, "sat": 5,
    "sunday": 6, "sun": 6,
}

MONTHS = {}
for _i in range(1, 13):
    MONTHS[calendar.month_name[_i].lower()] = _i
    MONTHS[calendar.month_abbr[_i].lower()] = _i
MONTHS["sept"] = 9

_MONTH_RE = "|".join(sorted(MONTHS, key=len, reverse=True))
_WEEKDAY_RE = "|".join(sorted(WEEKDAYS, key=len, reverse=True))

_ISO = re.compile(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b")
_NUMERIC = re.compile(r"\b(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?\b")
_MONTH_DAY = re.compile(
    rf"\b({_MONTH_RE})\.?\s+(\d{{1,2}})(?:st|nd|rd|th)?\b(?:,?\s*(\d{{4}}))?"
)
_DAY_MONTH = re.compile(
    rf"\b(\d{{1,2}})(?:st|nd|rd|th)?\s+(?:of\s+)?({_MONTH_RE})\b\.?(?:,?\s*(\d{{4}}))?"
)
_IN_N = re.compile(r"\bin\s+(\d{1,3}|a|an|one|two|three|four|five|six|seven)\s+(day|days|week|weeks)\b")
_WEEKDAY = re.compile(rf"\b(next|this|on|by|due)?\s*({_WEEKDAY_RE})\b")

_WORD_NUM = {"a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4,
             "five": 5, "six": 6, "seven": 7}


def _safe_date(year: int, month: int, day: int) -> Optional[date]:
    try:
        return date(year, month, day)
    except ValueError:
        return None


def _roll_forward(candidate: Optional[date], today: date, year_given: bool) -> Optional[date]:
    """If no year was given and the date already passed, assume next year."""
    if candidate and not year_given and candidate < today:
        return _safe_date(candidate.year + 1, candidate.month, candidate.day)
    return candidate


def parse_deadline(text: str, today: Optional[date] = None) -> Optional[date]:
    """Return the first deadline found in ``text`` or None."""
    today = today or date.today()
    t = text.lower()

    # Explicit dates first: they are unambiguous.
    m = _ISO.search(t)
    if m:
        return _safe_date(int(m.group(1)), int(m.group(2)), int(m.group(3)))

    m = _MONTH_DAY.search(t)
    if m:
        year = int(m.group(3)) if m.group(3) else today.year
        return _roll_forward(_safe_date(year, MONTHS[m.group(1)], int(m.group(2))), today, bool(m.group(3)))

    m = _DAY_MONTH.search(t)
    if m:
        year = int(m.group(3)) if m.group(3) else today.year
        return _roll_forward(_safe_date(year, MONTHS[m.group(2)], int(m.group(1))), today, bool(m.group(3)))

    m = _NUMERIC.search(t)
    if m:  # US-style month/day
        year_s = m.group(3)
        year = today.year
        if year_s:
            year = int(year_s) + (2000 if len(year_s) == 2 else 0)
        return _roll_forward(_safe_date(year, int(m.group(1)), int(m.group(2))), today, bool(year_s))

    # Relative phrases.
    if re.search(r"\bday after tomorrow\b", t):
        return today + timedelta(days=2)
    if re.search(r"\b(tomorrow|tmrw|tmr)\b", t):
        return today + timedelta(days=1)
    if re.search(r"\b(today|tonight|asap|eod|end of (the )?day)\b", t):
        return today

    m = _IN_N.search(t)
    if m:
        n = _WORD_NUM.get(m.group(1)) or int(m.group(1))
        return today + timedelta(days=n * (7 if m.group(2).startswith("week") else 1))

    if re.search(r"\b(end of (the )?week|eow)\b", t):
        return today + timedelta(days=(4 - today.weekday()) % 7)
    if re.search(r"\b(end of (the )?month|eom)\b", t):
        return date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
    if re.search(r"\b(this )?weekend\b", t):
        return today + timedelta(days=(5 - today.weekday()) % 7)
    if re.search(r"\bnext week\b", t):
        return today + timedelta(days=7 - today.weekday())
    if re.search(r"\bnext month\b", t):
        y, mo = (today.year + 1, 1) if today.month == 12 else (today.year, today.month + 1)
        return date(y, mo, 1)

    m = _WEEKDAY.search(t)
    if m:
        target = WEEKDAYS[m.group(2)]
        delta = (target - today.weekday()) % 7
        if m.group(1) == "next":
            # "next friday" = the friday of next calendar week
            delta = (7 - today.weekday()) + target
        elif delta == 0 and m.group(1) != "this":
            delta = 7
        return today + timedelta(days=delta)

    return None
