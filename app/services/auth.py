"""Sign-up and Name Your Rat validation rules (services layer).

Services know the rules and never import `request`. The validators in
this file are pure functions; other auth services (register_user,
claim_username in issue #15) will read and write the database.
"""

import string

EMAIL_MAX_LENGTH = 255
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 16
USERNAME_ALLOWED_CHARACTERS = string.ascii_lowercase + string.digits + "_"


def normalize_email(raw: str) -> str:
    """Return the email without surrounding spaces, in lowercase.

    Example: "  Klara@X.com " -> "klara@x.com"
    """
    return raw.strip().lower()


def validate_signup(email: str, password: str, confirm: str) -> list[str]:
    """Check the sign-up form and return every error found.

    An empty list means the form is valid. Whether the email is already
    taken is checked later, in register_user (issue #15).
    """
    errors = []

    if not _is_valid_email(email.strip()):
        errors.append("Enter a valid email address.")

    if not PASSWORD_MIN_LENGTH <= len(password) <= PASSWORD_MAX_LENGTH:
        errors.append(
            f"Password must be between {PASSWORD_MIN_LENGTH} and "
            f"{PASSWORD_MAX_LENGTH} characters."
        )

    if confirm != password:
        errors.append("Passwords don't match.")

    return errors


def validate_username(raw: str) -> list[str]:
    """Check a Name Your Rat username and return every error found.

    Rules: 3-16 characters after stripping spaces, only lowercase letters,
    digits and _. Whether the name is already taken is checked later, in
    claim_username (issue #15).
    """
    username = raw.strip()
    errors = []

    if not USERNAME_MIN_LENGTH <= len(username) <= USERNAME_MAX_LENGTH:
        errors.append(
            f"Your rat's name must be between {USERNAME_MIN_LENGTH} and "
            f"{USERNAME_MAX_LENGTH} characters."
        )

    if not all(character in USERNAME_ALLOWED_CHARACTERS for character in username):
        errors.append("Use only lowercase letters, digits and _.")

    return errors


def _is_valid_email(email: str) -> bool:
    """Present, at most 255 characters, one @, and a . after it."""
    if not email or len(email) > EMAIL_MAX_LENGTH:
        return False
    if email.count("@") != 1:
        return False
    local_part, domain = email.split("@")
    return bool(local_part) and "." in domain
