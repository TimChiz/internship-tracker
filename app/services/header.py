"""What the shared header shows on every logged-in page, and when its rat races."""

from dataclasses import dataclass

from app.models import Application, User
from app.services.stats import count_sent, was_sent

DEFAULT_RAT_IMAGE = "images/rat-default.png"  # every user's rat until choosing one of 8 is built (issue #38)


@dataclass(frozen=True)
class HeaderData:
    """Everything templates/components/app_header.html needs. Routes pass it to the page as `header`.

    Attributes:
        username: the name shown in big type.
        rat_image: the rat picture's path inside app/static, for url_for('static', filename=...).
        sent_count: the number shown beside the rat: every application the user has ever sent.
    """

    username: str
    rat_image: str
    sent_count: int


def get_header_data(user: User) -> HeaderData:
    """Build the header for this user."""
    return HeaderData(
        username=user.username,
        rat_image=DEFAULT_RAT_IMAGE,
        sent_count=count_sent(user),
    )


def starts_race(sent_before: bool, application: Application) -> bool:
    """Say whether a save should play the racing rat: only when it marks the application as sent for the first time.

    That happens when it leaves "To apply", from the Add popup, the status menu or the edit page.
    Later changes, like Applied to Interviewing, or an offer or rejection, don't race again.

    sent_before: was_sent(application) from before the save.
    """
    return not sent_before and was_sent(application)
