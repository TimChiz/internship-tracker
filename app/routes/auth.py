"""Auth routes and the decorator that protects every other page."""

from functools import wraps

from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.services.auth import authenticate, claim_username, register_user, validate_signup
from app.services.errors import AuthError

auth = Blueprint("auth", __name__)


def show_form_again(template, errors, **refill):
    """Show a form again with its errors, as a 400 (the input was wrong).

    refill puts back what the user typed, e.g. email="rat@x.com".
    Never pass the password here, so it never ends up in the page.
    """
    return render_template(template, errors=errors, **refill), 400


def page_after_login(user):
    """Where to go after logging in: Name Your Rat if there's no username yet, otherwise the applications.

    Always a fixed page, never ?next= from the link, so a login link can't send people to another site.
    """
    if user.username is None:
        return url_for("auth.name_your_rat")
    return url_for("applications.index")


@auth.route("/login", methods=["GET", "POST"])
def login():
    """Show the log in screen, and log the user in when the form is sent."""
    if request.method == "GET":
        return render_template("auth/login.html")

    email = request.form.get("email", "")
    user = authenticate(email, request.form.get("password", ""))
    if user is None:
        # one message for both cases, so the page doesn't reveal which emails have an account
        return show_form_again("auth/login.html", ["Email or password is incorrect."], email=email)

    login_user(user)
    return redirect(page_after_login(user))


@auth.route("/register", methods=["GET", "POST"])
def register():
    """Show the create account screen, and create the account when the form is sent."""
    if request.method == "GET":
        return render_template("auth/register.html")

    email = request.form.get("email", "")
    password = request.form.get("password", "")

    errors = validate_signup(email, password, request.form.get("confirm", ""))
    if errors:
        return show_form_again("auth/register.html", errors, email=email)

    try:
        user = register_user(email, password)
    except AuthError as error:
        # the email is already registered
        return show_form_again("auth/register.html", [str(error)], email=email)

    login_user(user)
    return redirect(url_for("auth.name_your_rat"))


@auth.route("/logout", methods=["POST"])
def logout():
    """Log the user out and go to the log in screen.

    POST only, so a link or the browser preloading /logout can't log anyone out
    (just opening /logout gives 405).
    """
    logout_user()
    return redirect(url_for("auth.login"))


@auth.route("/name-your-rat", methods=["GET", "POST"])
@login_required
def name_your_rat():
    """Show the Name Your Rat screen, and save the username when the form is sent.

    Only needs a logged-in user. Someone who already has a username goes to their applications.
    """
    if current_user.username is not None:
        return redirect(url_for("applications.index"))

    if request.method == "GET":
        return render_template("auth/name_your_rat.html")

    username = request.form.get("username", "")
    errors = claim_username(current_user, username)
    if errors:
        return show_form_again("auth/name_your_rat.html", errors, username=username)

    return redirect(url_for("applications.index"))


def username_required(view):
    """Only show the page to a logged-in user who has picked a username.

    - logged out -> /login
    - logged in, no username yet -> /name-your-rat
    - otherwise -> the page

    Put it under @<blueprint>.route on every page outside auth.
    """

    @wraps(view)
    def wrapped_view(*args, **kwargs):
        """Check the user first, then run the real page (view) with the same arguments."""
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        if current_user.username is None:
            return redirect(url_for("auth.name_your_rat"))
        return view(*args, **kwargs)

    return wrapped_view