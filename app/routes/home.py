"""The main page (/): sends people to the right place."""

from flask import Blueprint, redirect, url_for
from flask_login import current_user

home = Blueprint("home", __name__)


@home.route("/")
def index():
    """Logged in -> /applications, logged out -> /login."""
    if current_user.is_authenticated:
        return redirect(url_for("applications.index"))
    return redirect(url_for("auth.login"))