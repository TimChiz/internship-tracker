"""Sign-up and Name Your Rat validation rules (services layer).

Services know the rules and never import `request`. The validators are
pure functions; register_user, authenticate and claim_username read and
write the database through app/repositories/users.py.
"""

import string

from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from app.models import User
from app.repositories.users import UserRepository, add_user
from app.services.errors import AuthError

EMAIL_MAX_LENGTH = 255
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 16
USERNAME_ALLOWED_CHARACTERS = string.ascii_letters + string.digits + "_"  # a-z, A-Z, 0-9 and _


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

    Rules: 3-16 characters after stripping spaces, only letters, digits
    and _. Capitals are allowed and kept as typed. Whether the name is
    already taken (ignoring capitals) is checked later, in claim_username
    (issue #15).
    """
    username = raw.strip()
    errors = []

    if not USERNAME_MIN_LENGTH <= len(username) <= USERNAME_MAX_LENGTH:
        errors.append(
            f"Your rat's name must be between {USERNAME_MIN_LENGTH} and "
            f"{USERNAME_MAX_LENGTH} characters."
        )

    if not all(character in USERNAME_ALLOWED_CHARACTERS for character in username):
        errors.append("Use only letters, digits and _.")

    return errors


def register_user(email: str, password: str) -> User:
    """Create a new account and return it.

    The email is normalized first, so "Klara@X.com" and "klara@x.com" count
    as the same account. The password is stored only as a hash.
    Raises AuthError if the email is already registered.
    """
    email = normalize_email(email)

    if UserRepository.by_email(email) is not None:
        raise AuthError("An account with that email already exists.")

    user = User(email=email, password_hash=generate_password_hash(password))
    add_user(user)
    db.session.commit()
    return user


def authenticate(email: str, password: str) -> User | None:
    """Return the user if the email and password match, otherwise None.

    Unknown email and wrong password both return None, so the login page
    can't reveal which accounts exist.
    """
    user = UserRepository.by_email(normalize_email(email))

    if user is None or not check_password_hash(user.password_hash, password):
        return None
    return user


def claim_username(user: User, raw: str) -> list[str]:
    """Give the user a Name Your Rat username and return any errors.

    An empty list means the name was saved. The name is validated first;
    if it's taken (by someone else, ignoring case) nothing is saved.
    """
    errors = validate_username(raw)
    if errors:
        return errors

    username = raw.strip()
    existing = UserRepository.by_username(username)
    if existing is not None and existing.id != user.id:
        return ["That name is taken."]

    user.username = username
    db.session.commit()
    return []


def _is_valid_email(email: str) -> bool:
    """Present, at most 255 characters, one @, and a . after it."""
    if not email or len(email) > EMAIL_MAX_LENGTH:
        return False
    if email.count("@") != 1:
        return False
    local_part, domain = email.split("@")
    return bool(local_part) and "." in domain
