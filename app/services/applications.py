"""Business rules for the Applications table: checking the Add form, saving a new
application, and grouping and sorting applications into the table's sections.

The rules come from product/applications_table_plan.md (issue #20).
"""

from datetime import date, datetime

from app import db
from app.clock import app_now
from app.constants import SECTIONS, STATUS_LABELS, STATUS_OPTIONS, TO_APPLY_STATUSES
from app.models import Application, User
from app.repositories.applications import ApplicationRepository, add_application
from app.services.deadlines import format_date, get_deadline_label
from app.services.tracker import change_application_status

# Same limits as the columns in app/models.py
MAX_NAME_LENGTH = 120
MAX_URL_LENGTH = 2048

# The form fields the Add popup sends, so routes and templates use the same names
FORM_FIELDS = ("company", "role", "url", "status", "deadline", "is_rolling", "notes")


def validate_application_form(form: dict) -> tuple[dict, dict]:
    """Check the Add form and return (values, errors).

    form: the submitted fields, e.g. request.form.
    values: the cleaned values, ready to save. Only complete when errors is empty.
    errors: one message per field that has a problem, e.g. {"company": "Add a company."}.
        An empty dict means the form is fine.
    """
    errors = {}

    company = form.get("company", "").strip()
    role = form.get("role", "").strip()
    url = form.get("url", "").strip()
    status = form.get("status", "to_do")
    raw_deadline = form.get("deadline", "").strip()
    notes = form.get("notes", "").strip()

    for field, value, missing_message in (
        ("company", company, "Add a company."),
        ("role", role, "Add a role."),
    ):
        if not value:
            errors[field] = missing_message
        elif len(value) > MAX_NAME_LENGTH:
            errors[field] = f"Keep it to {MAX_NAME_LENGTH} characters or fewer."

    if url and not url.lower().startswith(("http://", "https://")):
        errors["url"] = "Links start with http:// or https://."
    elif len(url) > MAX_URL_LENGTH:
        errors["url"] = f"Keep the link to {MAX_URL_LENGTH} characters or fewer."

    if status not in STATUS_OPTIONS:
        errors["status"] = "Pick a status from the list."

    # A date input sends "" when it's empty, or a date like "2026-11-20"
    deadline = None
    if raw_deadline:
        try:
            deadline = date.fromisoformat(raw_deadline)
        except ValueError:
            errors["deadline"] = "Enter a date like 2026-11-20."

    values = {
        "company": company,
        "role": role,
        "url": url or None,
        "status": status,
        "deadline": deadline,
        # A checkbox only appears in the form when it's ticked
        "is_rolling": "is_rolling" in form,
        "notes": notes,
    }
    return values, errors


def create_application(user: User, values: dict) -> Application:
    """Save a new application for this user and return it.

    values: the cleaned values from validate_application_form.
    If it's added as already applied (or further), applied_at is set now,
    so it counts on this week's leaderboard.
    """
    # Route initial status changes through the same rule used for later updates.
    application = Application(
        user_id=user.id,
        **{**values, "status": TO_APPLY_STATUSES[0]},
    )
    change_application_status(application, values["status"], app_now())

    add_application(application)
    db.session.commit()
    return application


def build_row(application: Application, today: date) -> dict:
    """Turn one application into what a table row shows."""
    label, urgency = get_deadline_label(
        application.deadline, application.is_rolling, application.status, today
    )
    # "Rolling" already shows in the deadline cell itself, so don't repeat it underneath
    if label == "Rolling":
        label, urgency = None, None

    if application.deadline is not None:
        deadline_text = format_date(application.deadline)
    elif application.is_rolling:
        deadline_text = "Rolling"
    else:
        deadline_text = "No deadline"

    return {
        "id": application.id,
        "name": f"{application.company} - {application.role}",
        "url": application.url,
        "status": application.status,
        "status_label": STATUS_LABELS[application.status],
        "notes": application.notes,
        "deadline_text": deadline_text,
        "has_deadline": application.deadline is not None,
        "label": label,
        "urgency": urgency,
    }


def _to_apply_sort_key(application: Application, today: date) -> tuple:
    """Most urgent first: dated (soonest first), rolling, no deadline, then overdue."""
    if application.deadline is None:
        group = 1 if application.is_rolling else 2
        return (group, date.max, application.created_at)
    if application.deadline < today:
        return (3, application.deadline, application.created_at)
    return (0, application.deadline, application.created_at)


def _applied_sort_key(application: Application) -> tuple:
    """Most recently applied first. Rows with no applied_at go last."""
    applied_at = application.applied_at or datetime.min
    return (applied_at, application.created_at)


def group_applications(applications: list[Application], today: date) -> list[dict]:
    """Split applications into the table's sections, sorted, as the template needs them.

    Returns one dict per section in SECTIONS order, e.g.
    {"id": "to_apply", "title": "To apply", "rows": [...]}.
    """
    sorted_by_section = {
        "to_apply": lambda apps: sorted(apps, key=lambda app: _to_apply_sort_key(app, today)),
        "applied": lambda apps: sorted(apps, key=_applied_sort_key, reverse=True),
        "closed": lambda apps: sorted(apps, key=lambda app: app.updated_at, reverse=True),
    }

    sections = []
    for section_id, title, statuses in SECTIONS:
        in_section = [app for app in applications if app.status in statuses]
        ordered = sorted_by_section[section_id](in_section)
        sections.append({
            "id": section_id,
            "title": title,
            "rows": [build_row(app, today) for app in ordered],
        })
    return sections


def get_table_sections(user: User) -> list[dict]:
    """Return this user's applications grouped and sorted for the table."""
    applications = ApplicationRepository.for_user(user.id)
    return group_applications(applications, app_now().date())
