"""Business rules for quick-adding and updating internship applications."""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Protocol
from urllib.parse import urlsplit

from app.constants import SECTIONS, STATUS_OPTIONS


_QUICK_ADD_LINK = re.compile(r"https?://\S+", re.IGNORECASE)
_QUICK_ADD_SEPARATOR = re.compile(r"\s+[-–—]\s+")
_TO_APPLY_STATUSES = SECTIONS[0][2]


@dataclass(frozen=True)
class QuickAddResult:
    """Fields parsed from the quick-add box."""

    company: str = ""
    role: str = ""
    link: str = ""


class StatusApplication(Protocol):
    status: str
    applied_at: Optional[datetime]


def parse_quick_add(value: str) -> QuickAddResult:
    """Parse a URL or company/role text without fetching external pages."""
    text = value.strip()
    if not text:
        raise ValueError("Type a company and role, or paste a link.")

    if _QUICK_ADD_LINK.fullmatch(text):
        return QuickAddResult(link=text)

    parts = _QUICK_ADD_SEPARATOR.split(text, maxsplit=1)
    company = parts[0].strip()
    role = parts[1].strip() if len(parts) == 2 else ""

    # Keep parsed values within the application table's 120-character limits.
    if len(company) > 120:
        raise ValueError("Company must be 120 characters or fewer.")
    if len(role) > 120:
        raise ValueError("Role must be 120 characters or fewer.")

    return QuickAddResult(company=company, role=role)


def get_display_name(company: str, role: str, link: str) -> str:
    """Build the application name from its text fields or the link's site."""
    company = company.strip()
    role = role.strip()

    if company and role:
        return f"{company} - {role}"
    if company or role:
        return company or role

    try:
        site = urlsplit(link.strip()).hostname or ""
    except ValueError:
        site = ""

    # The leading www. is presentation noise, not part of the site name.
    if site.lower().startswith("www."):
        site = site[4:]
    return site or "Untitled"


def change_application_status(
    application: StatusApplication, new_status: str, current_time: datetime
) -> None:
    """Update status and record the first time the application leaves To apply."""
    if new_status not in STATUS_OPTIONS:
        raise ValueError(f"Status must be one of: {', '.join(STATUS_OPTIONS)}.")

    # Leaving the To apply section counts once; later status changes preserve this time.
    if (
        application.status in _TO_APPLY_STATUSES
        and new_status not in _TO_APPLY_STATUSES
        and application.applied_at is None
    ):
        application.applied_at = current_time

    application.status = new_status
