"""Tests for the database tables in app/models.py.

Each test saves data and checks that the database stores it correctly, or rejects it
when it breaks one of our rules. The rules live in the database (UNIQUE, CHECK, NOT NULL),
so these tests prove the tables were created the way models.py describes.
"""

import unittest
from datetime import date

# The error SQLAlchemy raises when the database refuses to save a row because it
# breaks a rule: a duplicate in a UNIQUE column, a failed CHECK, a missing NOT NULL value.
from sqlalchemy.exc import IntegrityError

from app import create_app, db
from app.models import User, Application


class ModelsTest(unittest.TestCase):
    """Checks that the tables exist and that the database itself enforces our rules."""

    def setUp(self):
        """Runs before EACH test: a fresh app with its own empty in-memory database.

        create_app runs db.create_all(), so the tables already exist in that new database.
        """
        self.app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://"})
        # Database work needs to know which app it belongs to. push() makes this app
        # the "current" one until pop() in tearDown, so every line in the test can use db.
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        """Runs after EACH test, even a failed one: closes the database session and leaves the app context."""
        db.session.remove()
        self.ctx.pop()

    def add_user(self, email="a@x.com", username=None):
        """Helper, not a test (its name doesn't start with "test"): save one user and return it."""
        user = User(email=email, password_hash="not-a-real-hash", username=username)
        # add() stages the new row; commit() actually writes it to the database.
        db.session.add(user)
        db.session.commit()
        return user

    def test_new_application_gets_defaults(self):
        """An application saved with only a user gets the default values from models.py."""
        user = self.add_user()
        app_row = Application(user_id=user.id)   # every other column left out on purpose
        db.session.add(app_row)
        db.session.commit()

        self.assertEqual(app_row.status, "to_do")
        self.assertEqual(app_row.company, "")
        self.assertFalse(app_row.is_rolling)
        self.assertIsNone(app_row.applied_at)       # not sent yet
        self.assertIsNotNone(app_row.created_at)    # filled in by default=app_now

    def test_application_can_store_a_deadline(self):
        """A deadline is stored and read back as a date."""
        user = self.add_user()
        db.session.add(Application(user_id=user.id, deadline=date(2026, 11, 13)))
        db.session.commit()

        # .query.first() reads the row back from the database.
        self.assertEqual(Application.query.first().deadline, date(2026, 11, 13))

    def test_unknown_status_is_rejected(self):
        """The CHECK constraint rejects a status that isn't in STATUS_OPTIONS."""
        user = self.add_user()
        db.session.add(Application(user_id=user.id, status="done"))
        # "with self.assertRaises(X):" means: the test passes only if the code inside
        # raises X. If commit() succeeded, the test would fail.
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_duplicate_email_is_rejected(self):
        """Two users can't share an email (unique=True on User.email)."""
        self.add_user(email="a@x.com")
        db.session.add(User(email="a@x.com", password_hash="not-a-real-hash"))
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_duplicate_username_is_rejected(self):
        """Two users can't share a username (unique=True on User.username)."""
        self.add_user(email="a@x.com", username="tim_cheese")
        db.session.add(User(email="b@x.com", password_hash="not-a-real-hash", username="tim_cheese"))
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_several_users_without_username_are_allowed(self):
        """Users who haven't named their rat yet (username NULL) don't clash with each other."""
        self.add_user(email="a@x.com")
        self.add_user(email="b@x.com")
        self.assertEqual(User.query.count(), 2)

    def test_each_test_starts_with_an_empty_database(self):
        """Proves test isolation: no users are left over from the tests above."""
        self.assertEqual(User.query.count(), 0)