from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy() #the database object shared across the project (outside create_app so that in other files we can`from app import db`)
login_manager = LoginManager() #keeps track of who is logged in, through the session cookie

def create_app(test_config=None):
    """
    Builds a Flask app, configures it, and returns

    test_config: optional dir of test settings, that replaces the configures values, for example:
    - create_app() -> using the real database file
    - create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://"}) -> using a new empty db that lives only in RAM
    we need it so that we can run tests on a different/new db instead of our prod one, once we have the data of users etc.
    """

    app = Flask(__name__) 
    #creating the app

    app.config["SECRET_KEY"] = "dev" 
    #Flask uses SECRET_KEY to sign the session cookie -> this will have to be changed with a real secret when we deploy

    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    #the browser only sends our session cookie for requests that start on our own site, so other websites can't submit our forms as the logged-in user

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ratrace.sqlite"
    #specifying which database to connect to (sqlite: means an SQLite file; /// means a file relative to the instance/ folder (created by SQLAlchemy automatically))

    if test_config is not None:
        app.config.update(test_config)
    #if the caller passed test settings, then dict.update(a) copies every key/value pair from a into the dict

    db.init_app(app) 
    #connects the shared db object to this app

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    #where Flask-Login sends logged-out users (the login route from Noku's #23)

    from .repositories.users import UserRepository

    @login_manager.user_loader
    def load_user(user_id):
        """Return the logged-in user for this request, or None.

        Flask-Login stores only the user's id in the session cookie (as a
        string) and calls this on every request to turn it back into a User.
        """
        return UserRepository.by_id(int(user_id))

    from . import models
    with app.app_context():
        # Creates every table that doesn't exist yet. It never changes or deletes
        # a table that already exists, which is why changing a table later means
        # deleting the local database file.
        db.create_all()
    # create_all() needs to know WHICH app's database to use. app_context() says
    # "for the lines inside this block, the current app is this one".
    
    from .routes.home import home
    app.register_blueprint(home)

    from .routes.auth import auth
    app.register_blueprint(auth)

    from .routes.errors import errors
    app.register_blueprint(errors)
    from .routes.applications import applications
    app.register_blueprint(applications)

    return app