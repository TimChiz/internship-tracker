from datetime import date, datetime, time, timedelta

from app.constants import SECTIONS


TO_APPLY_STATUSES = next(
    statuses for section_id, _, statuses in SECTIONS if section_id == "to_apply"
)


def get_week_bounds(today: date) -> tuple[datetime, datetime]:
    """Return midnight Monday bounds for the week containing today."""
    # weekday() numbers Monday as 0, so subtracting it reaches this week's Monday.
    monday = today - timedelta(days=today.weekday())
    start = datetime.combine(monday, time.min)
    # The next Monday is the exclusive end of the week.
    end = start + timedelta(days=7)
    return start, end


def format_date(value: date) -> str:
    """Format a date as, for example, ``Oct 19, 2026``."""
    # %b is the locale's abbreviated month name (for example, "Oct").
    return f"{value:%b} {value.day}, {value.year}"


def get_deadline_label(
    deadline: date | None,
    is_rolling: bool,
    status: str,
    today: date,
) -> tuple[str | None, str | None]:
    """Return the deadline label and urgency for an application."""
    # Only statuses listed in the shared "To apply" section get deadline labels.
    if status not in TO_APPLY_STATUSES:
        return None, None

    if deadline is None:
        return ("Rolling", "normal") if is_rolling else (None, None)

    # A zero difference means the deadline is today; negative values are overdue.
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
