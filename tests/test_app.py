#tests for the app; run all tests from the repo root with `python -m unittest discover tests`
# -> discover searches the tests/ folder for files named test*.py, finds the classes that inherit from unittest.TestCase, and runs every method whose name starts with "test"

import unittest #Python's built-in testing framework (we'll learn about it later in the course)

from app import create_app

class CreateAppTest(unittest.TestCase):
    """
    Checks that create_app builds a correctly configured app

    TestCase is a group od related tests.
        each method starting with "test" is one separate test
        unittest reports pass/fail for each test
    """
    def test_default_config_uses_real_database_file(self):
        """ create_app() with no arguments uses the real SQLite file and is not in testing mode."""
        app = create_app()

        self.assertEqual(app.config["SQLALCHEMY_DATABASE_URI"], "sqlite:///ratrace.sqlite")
        self.assertFalse(app.testing)
        #app.testing is a shortcut for app.config["TESTING"]

    def test_test_config_replaces_default(self):
        """Settings passed in test_config replace the defaults: testing mode and an in-memory database."""
        app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://"})
        #TESTING=True makes Flask show errors directly in the test so that we don't end up with "500 Internal Server Error" pages
        #sqlite:// creates a new, fresh, empty database (in RAM) so that tests don't touch our prod db

        self.assertTrue(app.testing)
        self.assertEqual(app.config["SQLALCHEMY_DATABASE_URI"], "sqlite://")

    def test_home_page_responds(self):
        """Proves home blueprint is registered and works"""
        app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://"})

        client = app.test_client()
        response = client.get("/")
        #test_client() gives a fake browser and sends requests straight to the app
        # without starting a server or opening a network connection.

        self.assertEqual(response.status_code, 200)

    if __name__ == "__main__":
        unittest.main()