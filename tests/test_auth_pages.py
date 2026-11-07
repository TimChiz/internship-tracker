"""Tests for the log in and create account screens."""

import unittest

from app import create_app


class AuthPagesTest(unittest.TestCase):
    """Checks that each sign-on screen loads with its copy, logo and link to the other screen."""

    def setUp(self):
        """Create a fake browser for a test copy of the app, using a temporary in-memory database."""
        app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://"})
        self.client = app.test_client()

    def assert_page_contains(self, route, expected_texts):
        """Check that the route loads and that its HTML contains every expected piece of text."""
        response = self.client.get(route)
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        for text in expected_texts:
            self.assertIn(text, html)

    def test_login_page(self):
        """/login shows its copy, its fields and a link to /register."""
        self.assert_page_contains("/login", [
            "Welcome back",
            "Your rat is waiting at the starting line.",
            "LOG IN",
            'href="/register"',
        ])

    def test_register_page(self):
        """/register shows its copy, the password hint, the confirm password field and a link to /login."""
        self.assert_page_contains("/register", [
            "Join the race",
            'aria-describedby="reg-password-hint"',
            "At least 8 characters.",
            'name="email" autocomplete="email" placeholder="you@university.edu" required',
            'required minlength="8"',
            "Confirm password",
            'name="confirm"',
            "CREATE ACCOUNT",
            'href="/login"',
        ])

    def test_both_pages_share_the_stage(self):
        """Both screens show the real logo and the desert scene, and start in day mode."""
        for route in ("/login", "/register"):
            self.assert_page_contains(route, [
                "images/rat-race-logo.png",
                'class="desert-scene"',
                'data-theme="day"',
            ])

    def test_logo_and_fonts_are_served(self):
        """The logo and fonts the pages depend on are in the repo and load."""
        for path in (
            "images/rat-race-logo.png",
            "fonts/Pixelbasel.ttf",
            "fonts/Chava-Regular.ttf",
            "fonts/DMSans-Variable.ttf",
        ):
            with self.client.get(f"/static/{path}") as response:
                self.assertEqual(response.status_code, 200, path)


if __name__ == "__main__":
    unittest.main()
