from __future__ import annotations

import re
from calendar import monthrange
from datetime import date, timedelta

WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}

NUM_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}


def parse(s: str, today: date | None = None) -> date:
    if today is None:
        today = date.today()

    text = s.lower().strip()

    numeric_date_match = re.fullmatch(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})", text)
    if numeric_date_match:
        year = int(numeric_date_match.group(1))
        month = int(numeric_date_match.group(2))
        day = int(numeric_date_match.group(3))
        return date(year, month, day)

    if text == "today":
        return today
    if text == "tomorrow":
        return today + timedelta(days=1)
    if text == "yesterday":
        return today - timedelta(days=1)

    match = re.fullmatch(
        r"next (monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
        text,
    )
    if match:
        return _next_weekday(today, WEEKDAYS[match.group(1)])

    match = re.fullmatch(
        r"in (\d+|one|two|three|four|five|six|seven|eight|nine|ten) days?",
        text,
    )
    if match:
        return today + timedelta(days=_to_int(match.group(1)))

    match = re.fullmatch(
        r"(\d+|one|two|three|four|five|six|seven|eight|nine|ten) days? ago",
        text,
    )
    if match:
        return today - timedelta(days=_to_int(match.group(1)))

    match = re.fullmatch(
        r"(\d+|one|two|three|four|five|six|seven|eight|nine|ten) "
        r"(days?|weeks?|months?|years?) "
        r"(before|after) (.+)",
        text,
    )
    if match:
        amount = _to_int(match.group(1))
        unit = match.group(2)
        direction = match.group(3)
        base = parse(match.group(4), today)

        if direction == "before":
            amount *= -1

        return _add_time(base, amount, unit)

    absolute = _parse_absolute_date(text)
    if absolute is not None:
        return absolute

    raise ValueError(f"Could not parse date: {s}")

def _to_int(s: str) -> int:
    if s.isdigit():
        return int(s)
    return NUM_WORDS[s]


def _next_weekday(today: date, weekday: int) -> date:
    days_ahead = (weekday - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return today + timedelta(days=days_ahead)


def _parse_absolute_date(text: str) -> date | None:
    match = re.fullmatch(
        r"(january|february|march|april|may|june|july|august|september|october|november|december) "
        r"(\d{1,2})(?:st|nd|rd|th)?(?:,)? (\d{4})",
        text,
    )
    if not match:
        return None

    month = MONTHS[match.group(1)]
    day = int(match.group(2))
    year = int(match.group(3))
    return date(year, month, day)


def _add_time(base: date, amount: int, unit: str) -> date:
    if unit.startswith("day"):
        return base + timedelta(days=amount)
    if unit.startswith("week"):
        return base + timedelta(weeks=amount)
    if unit.startswith("month"):
        return _add_months(base, amount)
    if unit.startswith("year"):
        return _add_months(base, amount * 12)

    raise ValueError(f"Unknown unit: {unit}")


def _add_months(base: date, months: int) -> date:
    month_index = base.month - 1 + months
    year = base.year + month_index // 12
    month = month_index % 12 + 1
    day = min(base.day, monthrange(year, month)[1])
    return date(year, month, day)
