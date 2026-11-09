"""Database lookups for applications (repository layer).

Repositories only read from and add to the session. They never commit;
the service that calls them decides when to commit.
"""

from app import db
from app.models import Application


class ApplicationRepository:
    """Find applications in the database."""

    @staticmethod
    def for_user(user_id: int) -> list[Application]:
        """Return every application that belongs to this user, in no particular order."""
        return list(db.session.scalars(db.select(Application).where(Application.user_id == user_id)))


def add_application(application: Application) -> None:
    """Add a new application to the session. Does not commit."""
    db.session.add(application)
