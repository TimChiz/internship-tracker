from datetime import date, datetime, time, timedelta


def get_week_bounds(today: date) -> tuple[datetime, datetime]:
    """Return midnight Monday bounds for the week containing today."""
    monday = today - timedelta(days=today.weekday())
    start = datetime.combine(monday, time.min)
    end = start + timedelta(days=7)
    return start, end


def format_date(value: date) -> str:
    """Format a date as, for example, ``Oct 19, 2026``."""
    return f"{value:%b} {value.day}, {value.year}"


def get_deadline_label(
    deadline: date | None,
    is_rolling: bool,
    section: str,
    status: str,
    today: date,
) -> tuple[str | None, str | None]:
    """Return the deadline label and urgency for an application."""
    if section.strip().casefold() != "to apply" or status.strip().casefold() not in {
        "to do",
        "in progress",
    }:
        return None, None

    if deadline is None:
        return ("Rolling", "normal") if is_rolling else (None, None)

    days_left = (deadline - today).days
    if days_left < 0:
        return "Deadline passed", "overdue"
    if days_left == 0:
        return "Due today", "urgent"
    if days_left == 1:
        return "Due tomorrow", "urgent"
    if days_left <= 7:
        return f"{days_left} days left", "soon"
    return f"{days_left} days left", "normal"
