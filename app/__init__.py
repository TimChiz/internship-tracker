from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy() #the database object shared across the project (outside create_app so that in other files we can`from app import db`)

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

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ratrace.sqlite"
    #specifying which database to connect to (sqlite: means an SQLite file; /// means a file relative to the instance/ folder (created by SQLAlchemy automatically))

    if test_config is not None:
        app.config.update(test_config)
    #if the caller passed test settings, then dict.update(a) copies every key/value pair from a into the dict

    db.init_app(app) 
    #connects the shared db object to this app

    from .routes.home import home
    app.register_blueprint(home)

    return app