"""Tests for the error page shown for every HTTP error."""

import unittest

from flask import abort

from app import create_app


class ErrorPagesTest(unittest.TestCase):
    """Checks that errors show the error page with the right code, message and status."""

    def setUp(self):
        """Create a test copy of the app, with a few routes that fail on purpose."""
        self.app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://"})
        self.app.add_url_rule("/test/500", "test_500", lambda: abort(500))
        self.app.add_url_rule("/test/409", "test_409", lambda: abort(409))
        self.client = self.app.test_client()

    def assert_error_page(self, response, code, message):
        """Check that a response is the error page for this code and message."""
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, code)
        self.assertIn(f'<h1 class="rr-code">{code}</h1>', html)
        self.assertIn(f'<p class="rr-message">{message}</p>', html)
        self.assertIn(f"<title>{code} {message} · Rat Race</title>", html)

    def test_missing_page(self):
        """A page that doesn't exist shows 404 Page not found."""
        self.assert_error_page(self.client.get("/no-such-page"), 404, "Page not found")

    def test_wrong_method(self):
        """Sending a form to a page that doesn't accept one shows 405 Method not allowed."""
        self.assert_error_page(self.client.post("/login"), 405, "Method not allowed")

    def test_server_error(self):
        """A 500 error shows Internal server error."""
        self.assert_error_page(self.client.get("/test/500"), 500, "Internal server error")

    def test_unlisted_code_uses_fallback_message(self):
        """A code without its own message, such as 409, shows Something went wrong."""
        self.assert_error_page(self.client.get("/test/409"), 409, "Something went wrong")

    def test_crash_shows_500_page(self):
        """An unexpected crash outside of testing shows the 500 page, not Flask's default page."""
        app = create_app({"TESTING": False, "SQLALCHEMY_DATABASE_URI": "sqlite://"})
        app.add_url_rule("/test/crash", "test_crash", lambda: 1 / 0)

        with self.assertLogs(app.logger, level="ERROR"):
            response = app.test_client().get("/test/crash")

        self.assert_error_page(response, 500, "Internal server error")

    def test_page_has_logo_link_and_switch(self):
        """The logo links home, and the page has the day/night switch and the shared theme script."""
        html = self.client.get("/no-such-page").get_data(as_text=True)

        self.assertIn('href="/" aria-label="Rat Race home"', html)
        self.assertIn("images/rr-logo.png", html)
        self.assertIn('id="theme-toggle"', html)
        self.assertIn("js/theme.js", html)

    def test_logo_file_is_served(self):
        """The RR logo the page points to is in the repo and loads."""
        with self.client.get("/static/images/rr-logo.png") as response:
            self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
