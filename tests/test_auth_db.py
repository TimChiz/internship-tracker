"""Tests for register_user, authenticate and claim_username (issue #15).

Each test gets a fresh in-memory database, so tests never touch
ratrace.sqlite and never affect each other.
"""

import unittest

from app import create_app, db
from app.services.auth import authenticate, claim_username, register_user
from app.services.errors import AuthError

PASSWORD = "cheese123"


class AuthDatabaseTest(unittest.TestCase):
    def setUp(self):
        """Build a test app with an empty in-memory database."""
        self.app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://"})
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()

    def tearDown(self):
        """Throw the database away after each test."""
        db.session.remove()
        db.drop_all()
        self.context.pop()


class RegisterUserTest(AuthDatabaseTest):
    def test_stores_normalized_email(self):
        user = register_user("  Klara@X.com ", PASSWORD)
        self.assertEqual(user.email, "klara@x.com")

    def test_stored_hash_is_not_the_password(self):
        user = register_user("rat@example.com", PASSWORD)
        self.assertNotEqual(user.password_hash, PASSWORD)

    def test_same_email_with_different_caps_fails(self):
        register_user("rat@example.com", PASSWORD)
        with self.assertRaises(AuthError):
            register_user("RAT@Example.com", PASSWORD)


class AuthenticateTest(AuthDatabaseTest):
    def setUp(self):
        super().setUp()
        self.user = register_user("rat@example.com", PASSWORD)

    def test_right_password_returns_the_user(self):
        self.assertEqual(authenticate("Rat@Example.com", PASSWORD), self.user)

    def test_wrong_password_returns_none(self):
        self.assertIsNone(authenticate("rat@example.com", "wrong-password"))

    def test_unknown_email_returns_none(self):
        self.assertIsNone(authenticate("nobody@example.com", PASSWORD))


class ClaimUsernameTest(AuthDatabaseTest):
    def setUp(self):
        super().setUp()
        self.klara = register_user("klara@example.com", PASSWORD)
        self.ahmed = register_user("ahmed@example.com", PASSWORD)

    def test_valid_name_is_saved_stripped(self):
        self.assertEqual(claim_username(self.klara, "  klara_rat  "), [])
        self.assertEqual(self.klara.username, "klara_rat")

    def test_taken_name_is_rejected(self):
        claim_username(self.klara, "klara_rat")
        self.assertEqual(
            claim_username(self.ahmed, "klara_rat"), ["That name is taken."]
        )
        self.assertIsNone(self.ahmed.username)

    def test_uppercase_version_of_taken_name_is_rejected(self):
        """Capitals fail validation before the uniqueness check (rule from #22)."""
        claim_username(self.klara, "klara_rat")
        self.assertEqual(
            claim_username(self.ahmed, "Klara_Rat"),
            ["Use only lowercase letters, digits and _."],
        )

    def test_invalid_name_changes_nothing(self):
        self.assertNotEqual(claim_username(self.klara, "a-"), [])
        self.assertIsNone(self.klara.username)


if __name__ == "__main__":
    unittest.main()
