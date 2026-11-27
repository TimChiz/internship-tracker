from datetime import datetime
from app import db
from app.models import FriendRequest, User
from app.repositories.friends import FriendRepository
from app.repositories.users import UserRepository
from app.services.errors import NotFoundError
from app.services.auth import normalize_email


def find_user_by_username_or_email(text) -> User | None:
    """
    when a user types their friend in the "add a friend" box, this function will find the friend (or return None if it has typos or user doesn't exist)
    when @ -> email, otherwise username
    """
    cleaned = text.strip().lower()

    if "@" in cleaned:
        user = UserRepository.by_email(normalize_email(cleaned))
    else:
        user = UserRepository.by_username(cleaned)
    
    if user is None or user.username is None:
        return None
    return user

def send_friend_request(me, text, now) -> str:
    """
    Send a friend request from <me> to the user they typed.
    Returns the message to show to the person who is sending request (either "request sent" or "you are already friends" etc - appropriately based on context) 
    """
    potential_friend = find_user_by_username_or_email(text)
    if potential_friend is None:
        raise ValueError("No rat with that username or email exists.")
    if potential_friend.id == me.id:
        #The table would also refuse it, but handling this case here too with a friendly message instead of a crash
        raise ValueError("You can't add yourself to friends.")
    
    # Is there already a request between us, in either direction?
    existing = FriendRepository.get_request_between_users(me.id, potential_friend.id)

    if existing is not None:
        if existing.status == "accepted":
            raise ValueError(f"You're already friends with {potential_friend.username}.")
        if existing.from_user_id == me.id:
            raise ValueError(f"You already sent {potential_friend.username} a request.")
        
        #if I'm trying to send a request to a potential friend but there is a request between us already, and it is pending, and they sent it to me -> we both want to be friends -> so I'm accepting the request
        existing.status = "accepted"
        existing.responded_at = now
        db.session.commit()
        return f"You're now friends with {potential_friend.username}!"

    #No request yet in either direction -> create a pending one
    FriendRepository.add(
        FriendRequest(from_user_id=me.id, to_user_id=potential_friend.id, created_at=now)
    )
    db.session.commit()
    return f"Request sent to {potential_friend.username}."

def accept_request(me: User, request_id: int, now: datetime) -> None:
    """Accept a pending request that was sent TO me.

    Raises NotFoundError if it doesn't exist, isn't pending, or wasn't sent to me.
    """
    request = FriendRepository.get_request(request_id)

    # Only the recipient can accept. (The sender accepting their own request
    # would let anyone make anyone their friend.)
    if request is None or request.status != "pending" or request.to_user_id != me.id:
        raise NotFoundError()

    request.status = "accepted"
    request.responded_at = now
    db.session.commit()

def cancel_or_decline_request(me, request_id) -> None:
    """
    Delete a pending request: the sender cancels it, or the recipient declines it.

    Raises NotFoundError if it doesn't exist
    """

    request = FriendRepository.get_request(request_id)

    is_mine = request is not None and me.id in (request.from_user_id, request.to_user_id)
    if not is_mine or request.status != "pending":
        raise NotFoundError()
    FriendRepository.delete(request)

    db.session.commit()

def remove_friend(me, friend_id) -> None:
    """Deleting the accepted request between us (aka delete from friends).

    Raises NotFoundError if we aren't friends.
    """
    # The friendship can be stored in either direction, depending on who asked first, so will look it up both ways
    request = FriendRepository.get_request_between_users(me.id, friend_id)
    if request is None or request.status != "accepted":
        raise NotFoundError()

    FriendRepository.delete(request)
    db.session.commit()