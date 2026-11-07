"""Database lookups for users (repository layer).

Repositories only read from and add to the session. They never commit;
the service that calls them decides when to commit.
"""

from app import db
from app.models import User


class UserRepository:
    """Find users in the database. Every method returns a User or None."""

    @staticmethod
    def by_id(user_id: int) -> User | None:
        """Look up a user by primary key."""
        return db.session.get(User, user_id)

    @staticmethod
    def by_email(email: str) -> User | None:
        """Look up a user by email. Assumes the email is already normalized."""
        return db.session.scalar(db.select(User).where(User.email == email))

    @staticmethod
    def by_username(username: str) -> User | None:
        """Look up a user by username, ignoring upper/lower case."""
        return db.session.scalar(
            db.select(User).where(db.func.lower(User.username) == username.lower())
        )


def add_user(user: User) -> None:
    """Add a new user to the session. Does not commit."""
    db.session.add(user)
