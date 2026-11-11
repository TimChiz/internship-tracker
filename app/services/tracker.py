"""Business rules for quick-adding and updating internship applications."""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Protocol
from urllib.parse import urlsplit

from app import db
from app.constants import STATUS_OPTIONS, TO_APPLY_STATUSES
from app.models import Application
from app.repositories.applications import ApplicationRepository
from app.services.errors import NotFoundError


_QUICK_ADD_URL = re.compile(r"https?://\S+", re.IGNORECASE)
_QUICK_ADD_SEPARATOR = re.compile(r"\s+[-–—]\s+")


@dataclass(frozen=True)
class QuickAddResult:
    """Fields parsed from the quick-add box."""

    company: str = ""
    role: str = ""
    url: str = ""


class StatusApplication(Protocol):
    status: str
    applied_at: Optional[datetime]


def parse_quick_add(value: str) -> QuickAddResult:
    """Parse a URL or company/role text without fetching external pages."""
    text = value.strip()
    if not text:
        raise ValueError("Type a company and role, or paste a link.")

    if _QUICK_ADD_URL.fullmatch(text):
        return QuickAddResult(url=text)

    parts = _QUICK_ADD_SEPARATOR.split(text, maxsplit=1)
    company = parts[0].strip()
    role = parts[1].strip() if len(parts) == 2 else ""

    # Keep parsed values within the application table's 120-character limits.
    if len(company) > 120:
        raise ValueError("Company must be 120 characters or fewer.")
    if len(role) > 120:
        raise ValueError("Role must be 120 characters or fewer.")

    return QuickAddResult(company=company, role=role)


def get_display_name(company: str, role: str, url: str) -> str:
    """Build the application name from its text fields or the URL's site."""
    company = company.strip()
    role = role.strip()

    if company and role:
        return f"{company} - {role}"
    if company or role:
        return company or role

    try:
        site = urlsplit(url.strip()).hostname or ""
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
        application.status in TO_APPLY_STATUSES
        and new_status not in TO_APPLY_STATUSES
        and application.applied_at is None
    ):
        application.applied_at = current_time

    application.status = new_status


def create_application_quick_add(
    user_id: int, quick_add_text: str, current_time: datetime
) -> Application:
    """Parse and save a new to-do application for a user."""
    parsed = parse_quick_add(quick_add_text)
    application = Application(
        user_id=user_id,
        company=parsed.company,
        role=parsed.role,
        url=parsed.url or None,
        status=TO_APPLY_STATUSES[0],
        created_at=current_time,
        updated_at=current_time,
    )
    ApplicationRepository.add(application)
    db.session.commit()
    return application


def update_application_status(
    user_id: int,
    application_id: int,
    new_status: str,
    current_time: datetime,
) -> Application:
    """Change an owned application's status and save the update."""
    application = ApplicationRepository.get_for_user(user_id, application_id)
    if application is None:
        raise NotFoundError("Application not found.")

    change_application_status(application, new_status, current_time)
    application.updated_at = current_time
    db.session.commit()
    return application


def delete_application(user_id: int, application_id: int) -> None:
    """Delete an owned application."""
    application = ApplicationRepository.get_for_user(user_id, application_id)
    if application is None:
        raise NotFoundError("Application not found.")

    ApplicationRepository.delete(application)
    db.session.commit()
