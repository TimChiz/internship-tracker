from app import db
from app.models import FriendRequest
from sqlalchemy import and_, or_
from app.models import FriendRequest

class FriendRepository:

    @staticmethod
    def get_request_between_users(user_a_id, user_b_id):
        """
        Is there already a request between these two users (whoever sent it)?
        -> checks both a request from A->B and B->A
        """
        a_sent_to_b = and_(
            FriendRequest.from_user_id == user_a_id,
            FriendRequest.to_user_id == user_b_id,
        )

        b_sent_to_a = and_(
            FriendRequest.from_user_id == user_b_id,
            FriendRequest.to_user_id == user_a_id,
        )
        
        return FriendRequest.query.filter(or_(a_sent_to_b, b_sent_to_a)).first()
    #why static: @staticmethods have no self -> the repository has no data of its own to keep in `self` (stateless) since all the data is in the database (reached through db.session)


    @staticmethod
    def get_friend_ids(user_id: int):
        """
        Return the ids of this user's friends (accepted)
        """
        involves_user = or_(
            FriendRequest.from_user_id == user_id,
            FriendRequest.to_user_id == user_id,
        )
        accepted_requests = FriendRequest.query.filter(
            FriendRequest.status == "accepted",
            involves_user,
        ).all()

        friend_ids = []
        for request in accepted_requests:
            if request.from_user_id == user_id:
                friend_ids.append(request.to_user_id)
            else:
                friend_ids.append(request.from_user_id)
        return friend_ids