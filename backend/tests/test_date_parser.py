from datetime import date

import pytest

from app.date_parser import parse_deadline

TODAY = date(2026, 10, 13)  # a Tuesday


@pytest.mark.parametrize(
    "text,expected",
    [
        ("finish report today", date(2026, 10, 13)),
        ("call tonight", date(2026, 10, 13)),
        ("pay rent tomorrow", date(2026, 10, 14)),
        ("dentist day after tomorrow", date(2026, 10, 15)),
        ("gym on friday", date(2026, 10, 16)),
        ("submit by mon", date(2026, 10, 19)),
        ("standup tuesday", date(2026, 10, 20)),  # same weekday -> next week
        ("this tuesday sync", date(2026, 10, 13)),
        ("next friday party", date(2026, 10, 23)),
        ("next week dentist", date(2026, 10, 19)),
        ("clean garage this weekend", date(2026, 10, 17)),
        ("ship it end of week", date(2026, 10, 16)),
        ("in 3 days", date(2026, 10, 16)),
        ("in two weeks", date(2026, 10, 27)),
        ("taxes due 2026-11-01", date(2026, 11, 1)),
        ("rent 11/5", date(2026, 11, 5)),
        ("rent 1/5", date(2027, 1, 5)),  # passed this year -> next year
        ("trip 12/24/2026", date(2026, 12, 24)),
        ("party March 5", date(2027, 3, 5)),
        ("renew Oct 20th", date(2026, 10, 20)),
        ("renew Oct 5, 2026", date(2026, 10, 5)),
        ("5th of November", date(2026, 11, 5)),
        ("buy milk", None),
        ("2026-02-30 is invalid", None),
    ],
)
def test_parse_deadline(text, expected):
    assert parse_deadline(text, TODAY) == expected
