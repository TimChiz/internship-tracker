"""Routes for the Applications pages: the table and the Add popup (issue #29),
the status menu on each row, and the edit page and delete confirmation (issue #40)."""

from flask import Blueprint, abort, redirect, render_template, request, session, url_for
from flask_login import current_user

from app.clock import app_now
from app.constants import STATUS_LABELS, STATUS_OPTIONS
from app.routes.auth import username_required
from app.services.applications import (
    create_application,
    display_name,
    form_values_for,
    get_application,
    get_table_sections,
    update_application,
    validate_application_form,
)
from app.services.errors import NotFoundError
from app.services.header import get_header_data, starts_race
from app.services.stats import was_sent
from app.services.tracker import delete_application, update_application_status

applications = Blueprint("applications", __name__)

# (value, label) pairs for the Status dropdown, e.g. ("in_progress", "In progress")
STATUS_CHOICES = [(status, STATUS_LABELS[status]) for status in STATUS_OPTIONS]

RACE_SESSION_KEY = "play_race"  # set when an application is marked as sent; the next page plays the race once


def render_page(template, **context):
    """Render an Applications page with the shared header, and the racing rat if one is due."""
    return render_template(
        template,
        header=get_header_data(current_user),
        play_race=session.pop(RACE_SESSION_KEY, False),  # pop, so a reload doesn't race again
        **context,
    )


def race_if_just_sent(sent_before, application):
    """Queue the racing rat for the next page if this save just marked the application as sent."""
    if starts_race(sent_before, application):
        session[RACE_SESSION_KEY] = True


def render_table(form_values=None, form_errors=None, status_code=200):
    """Show the table. When form_errors is given, the Add popup shows already open with them."""
    sections = get_table_sections(current_user)
    page = render_page(
        "applications/index.html",
        sections=sections,
        has_applications=any(section["rows"] for section in sections),
        status_options=STATUS_CHOICES,
        form_values=form_values or {},
        form_errors=form_errors or {},
    )
    return page, status_code


def load_own_application(application_id):
    """Return the logged-in user's application, or stop with 404 if it isn't theirs or doesn't exist."""
    try:
        return get_application(current_user, application_id)
    except NotFoundError:
        abort(404)


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

    application = create_application(current_user, values)
    race_if_just_sent(False, application)  # a new application hasn't been sent before
    # Redirecting (instead of rendering) means refreshing the page won't add it twice
    return redirect(url_for("applications.index"))


@applications.route("/applications/<int:application_id>/status", methods=["POST"])
@username_required
def change_status(application_id):
    """Change one application's status from the status menu in its row, then go back to the table."""
    sent_before = was_sent(load_own_application(application_id))
    try:
        application = update_application_status(
            current_user.id, application_id, request.form.get("status", ""), app_now()
        )
    except NotFoundError:
        # Doesn't exist, or belongs to someone else. Both give 404, so nobody can
        # find out which ids exist by trying other users' rows.
        abort(404)
    except ValueError:
        # 400 = bad input: a status that isn't in STATUS_OPTIONS.
        abort(400)
    race_if_just_sent(sent_before, application)
    return redirect(url_for("applications.index"))


@applications.route("/applications/<int:application_id>/edit", methods=["GET", "POST"])
@username_required
def edit(application_id):
    """Show the edit page filled in with the saved application, and save its changes."""
    application = load_own_application(application_id)

    if request.method == "GET":
        form_values, errors, status_code = form_values_for(application), {}, 200
    else:
        values, errors = validate_application_form(request.form)
        if not errors:
            sent_before = was_sent(application)
            update_application(current_user, application_id, values)
            race_if_just_sent(sent_before, application)  # the same object, now updated
            return redirect(url_for("applications.index"))
        # 400 = bad input. The page shows again with the errors and what the user typed.
        form_values, status_code = request.form, 400

    page = render_page(
        "applications/edit.html",
        application_id=application_id,
        name=display_name(application),
        status_options=STATUS_CHOICES,
        form_values=form_values,
        form_errors=errors,
    )
    return page, status_code


@applications.route("/applications/<int:application_id>/delete", methods=["GET", "POST"])
@username_required
def delete(application_id):
    """Ask "Delete Stripe - SWE Intern?" first (GET), then delete once the user confirms (POST)."""
    application = load_own_application(application_id)

    if request.method == "POST":
        delete_application(current_user.id, application_id)
        return redirect(url_for("applications.index"))

    return render_page(
        "applications/delete.html",
        application_id=application_id,
        name=display_name(application),
    )
