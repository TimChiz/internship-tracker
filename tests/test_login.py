"""Tests for Flask-Login setup and username_required (issue #26).

A tiny test-only page uses the decorator, and a test-only route logs a
user in, so these tests don't depend on the real login page.
"""

import unittest

from flask_login import login_user

from app import create_app, db
from app.models import User
from app.routes.auth import username_required
from app.services.auth import claim_username, register_user


class UsernameRequiredTest(unittest.TestCase):
    def setUp(self):
        """Build a test app with an empty database and two test-only routes."""
        self.app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://"})

        @self.app.route("/test-only-page")
        @username_required
        def test_only_page():
            return "secret page"

        @self.app.route("/test-only-login/<int:user_id>")
        def test_only_login(user_id):
            login_user(db.session.get(User, user_id))
            return "logged in"

        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        self.client = self.app.test_client()
        self.user = register_user("rat@example.com", "cheese123")

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.context.pop()

    def test_logged_out_goes_to_login(self):
        response = self.client.get("/test-only-page")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith("/login"))

    def test_logged_in_without_username_goes_to_name_your_rat(self):
        self.client.get(f"/test-only-login/{self.user.id}")
        response = self.client.get("/test-only-page")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith("/name-your-rat"))

    def test_logged_in_with_username_sees_the_page(self):
        claim_username(self.user, "rat_one")
        self.client.get(f"/test-only-login/{self.user.id}")
        response = self.client.get("/test-only-page")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"secret page", response.data)

    def test_session_cookie_is_samesite_lax(self):
        self.assertEqual(self.app.config["SESSION_COOKIE_SAMESITE"], "Lax")


if __name__ == "__main__":
    unittest.main()
