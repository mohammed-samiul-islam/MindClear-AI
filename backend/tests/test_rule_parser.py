from datetime import date

import pytest

from app.rule_parser import classify_category, classify_priority, rule_based_parse, split_items

TODAY = date(2026, 10, 13)


@pytest.mark.parametrize(
    "text,expected",
    [
        ("pay the electricity bill", "Finance"),
        ("file taxes", "Finance"),
        ("book a dentist appointment", "Health"),
        ("go to the gym", "Health"),
        ("prepare slides for client meeting", "Work"),
        ("fix the login bug", "Work"),
        ("call mom", "Personal"),
        ("buy groceries", "Personal"),
        ("think about life", "Other"),
    ],
)
def test_classify_category(text, expected):
    assert classify_category(text) == expected


def test_priority_keywords():
    assert classify_priority("urgent: send invoice") == "High"
    assert classify_priority("maybe learn guitar someday") == "Low"
    assert classify_priority("water plants") == "Medium"


def test_priority_from_deadline():
    assert classify_priority("x", date(2026, 10, 14), TODAY) == "High"
    assert classify_priority("x", date(2026, 10, 18), TODAY) == "Medium"
    assert classify_priority("x", date(2026, 12, 1), TODAY) == "Low"


def test_split_items_handles_bullets_and_fillers():
    items = split_items("- I need to call mom\n* buy milk; pay rent. Remember to email Bob")
    assert items == ["Call mom", "Buy milk", "Pay rent", "Email Bob"]


def test_split_keeps_comma_before_year():
    assert split_items("renew passport by Oct 5, 2026") == ["Renew passport by Oct 5, 2026"]


def test_rule_based_parse_end_to_end():
    tasks = rule_based_parse("pay rent tomorrow, gym on friday", TODAY)
    assert [(t.category, t.priority, t.deadline) for t in tasks] == [
        ("Finance", "High", date(2026, 10, 14)),
        ("Health", "Medium", date(2026, 10, 16)),
    ]


def test_rule_based_parse_empty_raises():
    with pytest.raises(ValueError):
        rule_based_parse(" , ; \n")
