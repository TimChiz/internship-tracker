from flask import Blueprint

home = Blueprint("home", __name__)
@home.route("/")
def index():
    return "Rat Race is running. welcome to the home page :)"