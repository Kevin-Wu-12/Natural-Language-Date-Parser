from __future__ import annotations

import re
from calendar import monthrange
from datetime import date, timedelta

WEEKDAYS = {
    "monday": 0, "mon": 0,
    "tuesday": 1, "tue": 1, "tues": 1,
    "wednesday": 2, "wed": 2,
    "thursday": 3, "thu": 3, "thur": 3, "thurs": 3,
    "friday": 4, "fri": 4,
    "saturday": 5, "sat": 5,
    "sunday": 6, "sun": 6,
}

MONTHS = {
    "january": 1, "jan": 1,
    "february": 2, "feb": 2,
    "march": 3, "mar": 3,
    "april": 4, "apr": 4,
    "may": 5,
    "june": 6, "jun": 6,
    "july": 7, "jul": 7,
    "august": 8, "aug": 8,
    "september": 9, "sep": 9, "sept": 9,
    "october": 10, "oct": 10,
    "november": 11, "nov": 11,
    "december": 12, "dec": 12,
}

NUM_WORDS = {
    "a": 1, "an": 1, "one": 1,
    "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "ten": 10, "eleven": 11, "twelve": 12,
}

NUM_PATTERN = r"\d+|a|an|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve"


def parse(s: str, today: date | None = None) -> date:
    if today is None:
        today = date.today()

    text = _normalize(s)

    numeric = re.fullmatch(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})", text)
    if numeric:
        return date(int(numeric.group(1)), int(numeric.group(2)), int(numeric.group(3)))

    if text == "today":
        return today
    if text == "tomorrow":
        return today + timedelta(days=1)
    if text == "yesterday":
        return today - timedelta(days=1)

    match = re.fullmatch(rf"in ({NUM_PATTERN}) (days?|weeks?|months?|years?)", text)
    if match:
        return _add_time(today, _to_int(match.group(1)), match.group(2))

    match = re.fullmatch(rf"({NUM_PATTERN}) (days?|weeks?|months?|years?) ago", text)
    if match:
        return _add_time(today, -_to_int(match.group(1)), match.group(2))

    match = re.fullmatch(rf"({NUM_PATTERN}) (days?|weeks?|months?|years?) from now", text)
    if match:
        return _add_time(today, _to_int(match.group(1)), match.group(2))

    match = re.fullmatch(rf"({NUM_PATTERN}) (days?|weeks?|months?|years?) from (.+)", text)
    if match:
        return _add_time(parse(match.group(3), today), _to_int(match.group(1)), match.group(2))

    match = re.fullmatch(rf"({NUM_PATTERN}) (days?|weeks?|months?|years?) (after|before) (.+)", text)
    if match:
        amount = _to_int(match.group(1))
        if match.group(3) == "before":
            amount *= -1
        return _add_time(parse(match.group(4), today), amount, match.group(2))

    match = re.fullmatch(rf"({NUM_PATTERN}) (days?|weeks?|months?|years?) and ({NUM_PATTERN}) (days?|weeks?|months?|years?) (after|before|from) (.+)", text)
    if match:
        amount1 = _to_int(match.group(1))
        unit1 = match.group(2)
        amount2 = _to_int(match.group(3))
        unit2 = match.group(4)
        direction = match.group(5)
        base = parse(match.group(6), today)

        sign = -1 if direction == "before" else 1
        result = _add_time(base, sign * amount1, unit1)
        return _add_time(result, sign * amount2, unit2)

    match = re.fullmatch(r"next (\w+)", text)
    if match and match.group(1) in WEEKDAYS:
        return _next_weekday(today, WEEKDAYS[match.group(1)])

    match = re.fullmatch(r"last (\w+)", text)
    if match and match.group(1) in WEEKDAYS:
        return _last_weekday(today, WEEKDAYS[match.group(1)])

    absolute = _parse_absolute_date(text)
    if absolute is not None:
        return absolute

    raise ValueError(f"Could not parse date: {s}")


def _normalize(s: str) -> str:
    text = s.lower().strip()
    text = re.sub(r"\s+", " ", text)
    text = text.replace(".", "")
    return text


def _to_int(s: str) -> int:
    if s.isdigit():
        return int(s)
    return NUM_WORDS[s]


def _next_weekday(today: date, weekday: int) -> date:
    days_ahead = (weekday - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return today + timedelta(days=days_ahead)


def _last_weekday(today: date, weekday: int) -> date:
    days_back = (today.weekday() - weekday) % 7
    if days_back == 0:
        days_back = 7
    return today - timedelta(days=days_back)


def _parse_absolute_date(text: str) -> date | None:
    month_names = "|".join(MONTHS)

    match = re.fullmatch(
        rf"({month_names}) (\d{{1,2}})(?:st|nd|rd|th)?(?:,)? (\d{{4}})",
        text,
    )
    if match:
        return date(int(match.group(3)), MONTHS[match.group(1)], int(match.group(2)))

    match = re.fullmatch(
        rf"(\d{{1,2}})(?:st|nd|rd|th)? (?:of )?({month_names})(?:,)? (\d{{4}})",
        text,
    )
    if match:
        return date(int(match.group(3)), MONTHS[match.group(2)], int(match.group(1)))

    match = re.fullmatch(r"(\d{1,2})[-/](\d{1,2})[-/](\d{4})", text)
    if match:
        return date(int(match.group(3)), int(match.group(1)), int(match.group(2)))

    return None


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