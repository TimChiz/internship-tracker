"""Routes for the Applications page: the table and the Add popup (issue #29)."""

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user

from app.clock import app_now
from app.constants import STATUS_LABELS, STATUS_OPTIONS
from app.routes.auth import username_required
from app.services.applications import (
    create_application,
    get_table_sections,
    validate_application_form,
)
from app.services.errors import NotFoundError
from app.services.tracker import (
    create_application_quick_add,
    delete_application,
    update_application_status,
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

@applications.route("/applications/quick-add", methods=["POST"])
@username_required
def quick_add():
    """Save an application from the one-line quick-add box, then go back to the table."""
    try:
        # The service parses the text ("Stripe – SWE Intern" or a link) and saves it as To do.
        # The route asks the clock and passes the time in, like every service call.
        create_application_quick_add(current_user.id, request.form.get("entry", ""), app_now())
    except ValueError as error:
        # Blank text: the service raises ValueError with a message for the user,
        # e.g. "Type a company and role". flash() keeps it until the next page shows it.
        flash(str(error))
    # Redirect either way, so refreshing the page doesn't send the form again.
    return redirect(url_for("applications.index"))


@applications.route("/applications/<int:application_id>/status", methods=["POST"])
@username_required
def change_status(application_id):
    """Change one application's status from the dropdown, then go back to the table."""
    try:
        update_application_status(
            current_user.id, application_id, request.form.get("status", ""), app_now()
        )
    except NotFoundError:
        # Doesn't exist, or belongs to someone else. Both give 404, so nobody can
        # find out which ids exist by trying other users' rows.
        abort(404)
    except ValueError:
        # 400 = bad input: a status that isn't in STATUS_OPTIONS.
        abort(400)
    return redirect(url_for("applications.index"))


@applications.route("/applications/<int:application_id>/delete", methods=["POST"])
@username_required
def delete(application_id):
    """Delete one application, then go back to the table."""
    try:
        delete_application(current_user.id, application_id)
    except NotFoundError:
        abort(404)
    return redirect(url_for("applications.index"))