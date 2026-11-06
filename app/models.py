from . import db
from .clock import app_now
from .constants import STATUS_OPTIONS

#models.py is like the .sql files (CREATE TABLE etc) that we wrote in class, but written in Python - it creates the tables in sql for us 
#each class is one table, each db.Column is one column in this table

class User(db.Model):
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

class Application(db.Model):
    """One internship application of a user"""
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)

    #which user this application belongs to
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # default="": if no value is given, store an empty string. A user can paste
    # just a link if they are in a hurry ance come back to edit later, so company and role may start blank.
    company = db.Column(db.String(120), nullable=False, default="")
    role = db.Column(db.String(120), nullable=False, default="")
    url = db.Column(db.String(2048), nullable=True)

    # Must be one of STATUS_OPTIONS
    status = db.Column(db.String(20), nullable=False, default="to_do")

    # db.Date = a calendar day with no time ("2026-11-02") + some posting have a rolling deadline.
    deadline = db.Column(db.Date, nullable=True)
    is_rolling = db.Column(db.Boolean, nullable=False, default=False)

    # db.Text = text with no length limit, for free-form notes.
    notes = db.Column(db.Text, nullable=False, default="")

    # db.DateTime = a day plus a time. Set the first time the application is marked
    # as sent; the leaderboard counts these.
    applied_at = db.Column(db.DateTime, nullable=True)

    # default=utc_now passes the FUNCTION itself (no brackets), so SQLAlchemy calls it
    # at the moment each row is inserted. default=utc_now() WITH brackets would call it
    # once when this file loads, and every row would get that same, stale time.
    created_at = db.Column(db.DateTime, nullable=False, default=app_now)
    updated_at = db.Column(db.DateTime, nullable=False, default=app_now)

    # __table_args__: rules that apply to the whole table, not just one column.
    __table_args__ = (
        # CHECK constraint: the database itself rejects any status not in our list,
        # even if a bug somewhere in Python tries to save it
        db.CheckConstraint(f"status IN ({_allowed_statuses})", name="ck_applications_status"),
        
        # An index on (user_id, applied_at): lets the database find "this user's applications sent this week" without scanning every
        # row. The leaderboard runs exactly that query.
        db.Index("ix_applications_user_applied", "user_id", "applied_at"),
    )