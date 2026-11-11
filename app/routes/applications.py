"""Routes for the Applications page: the table and the Add popup (issue #29)."""

from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user

from app.constants import STATUS_LABELS, STATUS_OPTIONS
from app.routes.auth import username_required
from app.services.applications import (
    create_application,
    get_table_sections,
    validate_application_form,
)

applications = Blueprint("applications", __name__)


def render_table(form_values=None, form_errors=None, status_code=200):
    """Show the table. When form_errors is given, the Add popup shows already open with them."""
    sections = get_table_sections(current_user)
    page = render_template(
        "applications/index.html",
        sections=sections,
        has_applications=any(section["rows"] for section in sections),
        status_options=[(status, STATUS_LABELS[status]) for status in STATUS_OPTIONS],
        form_values=form_values or {},
        form_errors=form_errors or {},
    )
    return page, status_code


@applications.route("/applications")
@username_required
def index():
    """Show the logged-in user's applications, grouped into sections."""
    return render_table()


@applications.route("/applications/new", methods=["POST"])
@username_required
def new():
    """Save an application from the Add popup, then go back to the table."""
    values, errors = validate_application_form(request.form)
    if errors:
        # 400 = the request had bad input. The popup reopens with what the user typed.
        return render_table(form_values=request.form, form_errors=errors, status_code=400)

    create_application(current_user, values)
    # Redirecting (instead of rendering) means refreshing the page won't add it twice
    return redirect(url_for("applications.index"))
