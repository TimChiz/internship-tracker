from flask_login import UserMixin
from . import db
from .clock import utc_now
from .constants import STATUS_OPTIONS

#models.py is like the .sql files (CREATE TABLE etc) that we wrote in class, but written in Python - it creates the tables in sql for us 
#each class is one table, each db.Column is one column in this table

class User(UserMixin, db.Model):  
    """
    One person with an account
    """
    __tablename__ = "users"
    #the name of the table in the database

    id = db.Column(db.Integer, primary_key = True)
    #PK: id

    email = db.Column(db.String(255), unique=True, nullable=False)
    #String(255) - text of at most 255 characters; unique - so that no two accounts have the same email (DB will reject it); nullable=False, because every user must have an email

    password_hash = db.Column(db.String(255), nullable=False)

    username = db.Column(db.String(16), nullable=True)
    #nullable=True because me might want to save the user details to the table after the first page (email, password) and before the second page (choose username and avatar) so an account would be usernameless <if that's a word> for that mooment

db.Index("ix_users_username_lower", db.func.lower(User.username), unique=True)
#usernames must be unique, and we should save them all in lowercase. so we make a unique index 

_allowed_statuses = ", ". join(f" '{status}'" for status in STATUS_OPTIONS)

