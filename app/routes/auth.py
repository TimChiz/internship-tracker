"""Routes for the sign-on screens: log in and create account."""

from flask import Blueprint, render_template

auth = Blueprint("auth", __name__)


@auth.route("/login")
def login():
    """Show the log in screen."""
    return render_template("auth/login.html")


@auth.route("/register")
def register():
    """Show the create account screen."""
    return render_template("auth/register.html")
