"""One error page for every HTTP error, such as 404 Page not found or 500 Internal server error."""

from flask import Blueprint, render_template
from werkzeug.exceptions import HTTPException

errors = Blueprint("errors", __name__)

# The message shown under each error code. Codes not listed here show FALLBACK_MESSAGE.
ERROR_MESSAGES = {
    400: "Bad request",
    401: "Unauthorized",
    402: "Payment required",
    403: "Forbidden",
    404: "Page not found",
    405: "Method not allowed",
    408: "Request timeout",
    410: "Page gone",
    418: "I’m a teapot",
    429: "Too many requests",
    500: "Internal server error",
    501: "Not implemented",
    502: "Bad gateway",
    503: "Service unavailable",
    504: "Gateway timeout",
}
FALLBACK_MESSAGE = "Something went wrong"


def error_message(code):
    """Return the short message shown under an error code, such as "Page not found" for 404."""
    return ERROR_MESSAGES.get(code, FALLBACK_MESSAGE)


def render_error_page(code, message=None):
    """Return the error page for an error code, with the matching HTTP status.

    message is optional. Leave it out to use the standard message for that code.
    """
    page = render_template("error.html", code=code, message=message or error_message(code))
    return page, code


@errors.app_errorhandler(HTTPException)
def show_error_page(error):
    """Show the error page for any HTTP error the app raises, such as a missing page.

    Flask also sends unexpected crashes here as a 500 error, outside of testing.
    """
    return render_error_page(error.code or 500)
