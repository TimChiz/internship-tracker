"""The rats a user can pick on the Name Your Rat page, and saving their pick."""

from dataclasses import dataclass

from app import db
from app.models import User


@dataclass(frozen=True)
class Rat:
    """One rat a user can pick.

    Attributes:
        key: the short name saved in the database (users.rat), such as "classic".
        name: what screen readers call this rat, such as "Classic rat".
        image: the rat picture's path inside app/static, for url_for('static', filename=...).
    """

    key: str
    name: str
    image: str


RATS = (  # in the order the page flips through them; the finished app will have 8
    Rat("classic", "Classic rat", "images/rats/classic.png"),
    Rat("tough", "Tough rat", "images/rats/tough.png"),  # placeholder art until the real rats are drawn
)

DEFAULT_RAT = RATS[0]  # the rat the page opens on, and the rat of anyone who hasn't picked one


def get_rat(key: str | None) -> Rat:
    """Return the rat with this key, or the default rat if the key is empty or unknown."""
    for rat in RATS:
        if rat.key == key:
            return rat
    return DEFAULT_RAT


def choose_rat(user: User, rat: Rat) -> None:
    """Save this rat as the user's pick."""
    user.rat = rat.key
    db.session.commit()
