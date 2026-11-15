"""Numbers about a user's progress, such as how many applications they have sent."""

from app.models import Application, User
from app.repositories.applications import ApplicationRepository


def was_sent(application: Application) -> bool:
    """Say whether an application has been sent. applied_at is set the first time it leaves "To apply" and never cleared."""
    return application.applied_at is not None


def count_sent(user: User) -> int:
    """Return how many applications this user has ever sent, including ones that later got an offer or a rejection."""
    applications = ApplicationRepository.for_user(user.id)  # TODO: count in the database if lists get long
    return sum(was_sent(application) for application in applications)
