from datetime import date

import pytest

from nldate import parse

TODAY = date(2025, 11, 10)  # Monday


def test_today() -> None:
    assert parse("today", TODAY) == date(2025, 11, 10)


def test_tomorrow() -> None:
    assert parse("tomorrow", TODAY) == date(2025, 11, 11)


def test_yesterday() -> None:
    assert parse("yesterday", TODAY) == date(2025, 11, 9)


def test_next_tuesday() -> None:
    assert parse("next Tuesday", TODAY) == date(2025, 11, 11)


def test_next_monday_skips_to_following_week() -> None:
    assert parse("next Monday", TODAY) == date(2025, 11, 17)


def test_in_five_days() -> None:
    assert parse("in 5 days", TODAY) == date(2025, 11, 15)


def test_days_ago() -> None:
    assert parse("3 days ago", TODAY) == date(2025, 11, 7)


def test_absolute_date() -> None:
    assert parse("December 1st, 2025", TODAY) == date(2025, 12, 1)


def test_days_before_absolute_date() -> None:
    assert parse("5 days before December 1st, 2025", TODAY) == date(2025, 11, 26)


def test_weeks_after_tomorrow() -> None:
    assert parse("2 weeks after tomorrow", TODAY) == date(2025, 11, 25)


def test_month_after_end_of_month() -> None:
    assert parse("1 month after January 31st, 2025", TODAY) == date(2025, 2, 28)


def test_unparseable_input() -> None:
    with pytest.raises(ValueError):
        parse("sometime soon", TODAY)
