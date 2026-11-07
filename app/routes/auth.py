"""Auth routes and the decorator that protects every other page."""

from functools import wraps

from flask import redirect, Blueprint, render_template
from flask_login import current_user

auth = Blueprint("auth", __name__)

@auth.route("/login")
def login():
    """Show the log in screen."""
    return render_template("auth/login.html")

@auth.route("/register")
def register():
    """Show the create account screen."""
    return render_template("auth/register.html")

def username_required(view):
    """Only show the page to a logged-in user who has picked a username.

    - logged out -> /login
    - logged in, no username yet -> /name-your-rat
    - otherwise -> the page

    Put it under @<blueprint>.route on every page outside auth.
    """

    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect("/login")
        if current_user.username is None:
            return redirect("/name-your-rat")
        return view(*args, **kwargs)

    return wrapped_view