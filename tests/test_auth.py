"""Tests for the sign-up and username validators in app/services/auth.py.

Run all tests from the repo root with `python3 -m unittest discover tests`.
These are pure functions, so no app or database is needed.
"""

import unittest

from app.services.auth import (
    normalize_email,
    validate_signup,
    validate_username,
)

GOOD_EMAIL = "rat@example.com"
GOOD_PASSWORD = "cheese123"

EMAIL_ERROR = "Enter a valid email address."
PASSWORD_LENGTH_ERROR = "Password must be between 8 and 128 characters."
MISMATCH_ERROR = "Passwords don't match."
USERNAME_LENGTH_ERROR = "Your rat's name must be between 3 and 16 characters."
USERNAME_CHARACTERS_ERROR = "Use only letters, digits and _."


class NormalizeEmailTest(unittest.TestCase):
    def test_strips_spaces_and_lowercases(self):
        self.assertEqual(normalize_email("  Klara@X.com "), "klara@x.com")


class ValidateSignupTest(unittest.TestCase):
    def test_valid_form_has_no_errors(self):
        self.assertEqual(validate_signup(GOOD_EMAIL, GOOD_PASSWORD, GOOD_PASSWORD), [])

    def test_email_at_max_length_is_valid(self):
        email = "a" * 249 + "@x.com"  # 255 characters
        self.assertEqual(validate_signup(email, GOOD_PASSWORD, GOOD_PASSWORD), [])

    def test_bad_emails_give_only_the_email_error(self):
        too_long = "a" * 250 + "@x.com"  # 256 characters
        for email in (
            "",
            "   ",
            "ratexample.com",
            "rat@@example.com",
            "rat@example",
            "@example.com",
            too_long,
        ):
            with self.subTest(email=email):
                self.assertEqual(
                    validate_signup(email, GOOD_PASSWORD, GOOD_PASSWORD),
                    [EMAIL_ERROR],
                )

    def test_password_length_limits(self):
        for password, expected in (
            ("a" * 7, [PASSWORD_LENGTH_ERROR]),
            ("a" * 8, []),
            ("a" * 128, []),
            ("a" * 129, [PASSWORD_LENGTH_ERROR]),
        ):
            with self.subTest(length=len(password)):
                self.assertEqual(
                    validate_signup(GOOD_EMAIL, password, password), expected
                )

    def test_mismatched_confirm_gives_only_the_mismatch_error(self):
        self.assertEqual(
            validate_signup(GOOD_EMAIL, GOOD_PASSWORD, "cheese124"),
            [MISMATCH_ERROR],
        )

    def test_three_bad_fields_give_three_errors(self):
        self.assertEqual(
            validate_signup("not-an-email", "short", "different"),
            [EMAIL_ERROR, PASSWORD_LENGTH_ERROR, MISMATCH_ERROR],
        )


class ValidateUsernameTest(unittest.TestCase):
    def test_valid_usernames(self):
        for username in ("tim_cheese", "abc", "a" * 16, "  rat_1  "):
            with self.subTest(username=username):
                self.assertEqual(validate_username(username), [])

    def test_wrong_length_is_rejected(self):
        for username in ("ab", "a" * 17, "   "):
            with self.subTest(username=username):
                self.assertEqual(validate_username(username), [USERNAME_LENGTH_ERROR])

    def test_wrong_characters_are_rejected(self):
        for username in ("tim cheese", "tim-cheese", "rat!", "ratté"):
            with self.subTest(username=username):
                self.assertEqual(
                    validate_username(username), [USERNAME_CHARACTERS_ERROR]
                )

    def test_uppercase_is_allowed(self):
        """Capitals are fine. Klara and klara still can't both exist: claim_username checks that."""
        for username in ("Klara", "Tim_Cheese", "RAT"):
            with self.subTest(username=username):
                self.assertEqual(validate_username(username), [])

    def test_short_name_with_bad_character_gives_both_errors(self):
        self.assertEqual(
            validate_username("a-"),
            [USERNAME_LENGTH_ERROR, USERNAME_CHARACTERS_ERROR],
        )


if __name__ == "__main__":
    unittest.main()
