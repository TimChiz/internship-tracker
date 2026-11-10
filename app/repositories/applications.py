"""Database lookups and session operations for applications (repository layer).

Repositories never commit; the service that calls them decides when to commit.
"""

from datetime import datetime

from app import db
from app.models import Application


class ApplicationRepository:
    """Find and stage changes to applications in the database."""

    @staticmethod
    def for_user(user_id: int) -> list[Application]:
        """Return every application that belongs to this user, in no particular order."""
        return list(
            db.session.scalars(
                db.select(Application).where(Application.user_id == user_id)
            )
        )

    @staticmethod
    def get_for_user(user_id: int, application_id: int) -> Application | None:
        """Return an application only when it belongs to the given user."""
        return db.session.scalar(
            db.select(Application).where(
                # Check both IDs in one query so callers cannot access another user's row.
                Application.user_id == user_id,
                Application.id == application_id,
            )
        )

    @staticmethod
    def add(application: Application) -> None:
        """Add an application to the session. Does not commit."""
        db.session.add(application)

    @staticmethod
    def delete(application: Application) -> None:
        """Delete an application from the session. Does not commit."""
        db.session.delete(application)

    @staticmethod
    def count_sent_between(user_id: int, start: datetime, end: datetime) -> int:
        """Count this user's applications sent in [start, end)."""
        count = db.session.scalar(
            db.select(db.func.count(Application.id)).where(
                Application.user_id == user_id,
                # Use a half-open interval to avoid double-counting adjacent time windows.
                Application.applied_at >= start,
                Application.applied_at < end,
            )
        )
        return count or 0
