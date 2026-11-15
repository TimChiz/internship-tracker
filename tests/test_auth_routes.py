"""Tests for the auth routes and the main page (issue #34).

Each test drives the app the way a browser would: it submits the real
forms with the test client and follows where the app redirects.
"""

import unittest

from app import create_app, db
from app.models import User
from app.services.auth import claim_username, register_user

EMAIL = "rat@example.com"
PASSWORD = "cheese123"


class AuthRoutesTest(unittest.TestCase):
    def setUp(self):
        """Build a test app with an empty in-memory database and a fake browser."""
        self.app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://"})
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        """Throw the database away after each test."""
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.context.pop()

    def log_in(self, email=EMAIL, password=PASSWORD):
        """Submit the log in form and return the response."""
        return self.client.post("/login", data={"email": email, "password": password})

    def make_user(self, username=None):
        """Create an account (with a username if given) and return it."""
        user = register_user(EMAIL, PASSWORD)
        if username is not None:
            claim_username(user, username)
        return user


class RegisterTest(AuthRoutesTest):
    def test_valid_register_creates_user_and_goes_to_name_your_rat(self):
        response = self.client.post(
            "/register", data={"email": EMAIL, "password": PASSWORD, "confirm": PASSWORD}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith("/name-your-rat"))
        self.assertIsNotNone(db.session.query(User).filter_by(email=EMAIL).first())

    def test_bad_register_is_400_and_never_shows_the_password(self):
        response = self.client.post(
            "/register", data={"email": EMAIL, "password": "short7!", "confirm": "different"}
        )
        html = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 400)
        self.assertIn(EMAIL, html)  # the email is refilled
        self.assertNotIn("short7!", html)  # the password never is

    def test_email_already_registered_is_400(self):
        self.make_user()
        response = self.client.post(
            "/register", data={"email": EMAIL, "password": PASSWORD, "confirm": PASSWORD}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("An account with that email already exists.", response.get_data(as_text=True))


class LoginTest(AuthRoutesTest):
    def test_right_login_without_username_goes_to_name_your_rat(self):
        self.make_user()
        response = self.log_in()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith("/name-your-rat"))

    def test_right_login_with_username_goes_to_applications(self):
        self.make_user(username="rat_one")
        response = self.log_in()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith("/applications"))

    def test_wrong_password_is_400_with_one_message(self):
        self.make_user()
        response = self.log_in(password="wrong-password")
        html = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Email or password is incorrect.", html)
        self.assertNotIn("wrong-password", html)

    def test_unknown_email_gets_the_same_message(self):
        response = self.log_in(email="nobody@example.com")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Email or password is incorrect.", response.get_data(as_text=True))

    def test_next_in_the_link_is_ignored(self):
        self.make_user(username="rat_one")
        response = self.client.post(
            "/login?next=https://evil.example.com", data={"email": EMAIL, "password": PASSWORD}
        )
        self.assertTrue(response.location.endswith("/applications"))


class LogoutTest(AuthRoutesTest):
    def test_logout_by_submitting_goes_to_login(self):
        self.make_user(username="rat_one")
        self.log_in()
        response = self.client.post("/logout")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith("/login"))
        # really logged out: the main page now sends us to /login
        self.assertTrue(self.client.get("/").location.endswith("/login"))

    def test_just_opening_logout_is_405(self):
        self.assertEqual(self.client.get("/logout").status_code, 405)


class NameYourRatTest(AuthRoutesTest):
    def test_logged_out_goes_to_login(self):
        response = self.client.get("/name-your-rat")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)

    def test_page_loads_for_logged_in_user_without_username(self):
        self.make_user()
        self.log_in()
        self.assertEqual(self.client.get("/name-your-rat").status_code, 200)

    def test_taken_name_is_400(self):
        other = register_user("other@example.com", PASSWORD)
        claim_username(other, "rat_one")
        self.make_user()
        self.log_in()
        response = self.client.post("/name-your-rat", data={"username": "rat_one"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("That name is taken.", response.get_data(as_text=True))

    def test_valid_name_goes_to_applications(self):
        self.make_user()
        self.log_in()
        response = self.client.post("/name-your-rat", data={"username": "rat_one"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith("/applications"))
        self.assertEqual(db.session.query(User).filter_by(email=EMAIL).first().username, "rat_one")


class HomeTest(AuthRoutesTest):
    def test_logged_out_goes_to_login(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith("/login"))

    def test_logged_in_goes_to_applications(self):
        self.make_user(username="rat_one")
        self.log_in()
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith("/applications"))


if __name__ == "__main__":
    unittest.main()