import unittest
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from app import create_app, db
from app.models import FriendRequest, User
from app.repositories.friends import FriendRepository
from app.services.errors import NotFoundError
from app.services.friends import (
    accept_request,
    cancel_or_decline_request,
    remove_friend,
    send_friend_request,
)

NOW = datetime(2026, 11, 27, 12, 0)

class FriendsTest(unittest.TestCase):
    """The friend_requests table, FriendRepository, and the friend services."""

    def setUp(self):
        """Runs before EVERY test: a new app with an empty in-memory database."""
        # "sqlite://" = an in-memory database. It lives in RAM and disappears
        # when the test ends, so tests can't affect each other or your real
        # instance/ratrace.sqlite. create_app already runs db.create_all().
        self.app = create_app(
            {"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://"}
        )
        # Queries need an "app context" (Flask's "which app are we in?").
        # In the running app Flask creates one per request; in tests we push one ourselves.
        self.context = self.app.app_context()
        self.context.push()

        # Five users. Noku has no requests at all: the stranger.
        self.klara = self.make_user("klara")
        self.litong = self.make_user("litong")
        self.ahmed = self.make_user("ahmed")
        self.timu = self.make_user("timu")
        self.noku = self.make_user("noku")

    def tearDown(self):
        """Runs after EVERY test, even a failed one: clean up."""
        # remove() throws away the session, including one left broken by an
        # IntegrityError, so the next test starts clean.
        db.session.remove()
        self.context.pop()
    def make_user(self, username: str) -> User:
        """Save a user and return it (its id is set once it's committed)."""
        user = User(
            email=f"{username}@example.com",
            password_hash="not-a-real-hash",
            username=username,
        )
        db.session.add(user)
        db.session.commit()
        return user

    def add_request(self, sender: User, recipient: User, status: str = "pending") -> FriendRequest:
        """Save a friend request from sender to recipient and return it."""
        request = FriendRequest(
            from_user_id=sender.id, to_user_id=recipient.id, status=status
        )
        db.session.add(request)
        db.session.commit()
        return request

    def add_example_requests(self):
        """The example table: two friendships (one in each direction) and one pending request."""
        self.klara_to_litong = self.add_request(self.klara, self.litong, "accepted")
        self.ahmed_to_klara = self.add_request(self.ahmed, self.klara, "accepted")
        self.klara_to_timu = self.add_request(self.klara, self.timu, "pending")
    # --- get_request_between_users ---

    def test_finds_the_request_when_the_sender_is_given_first(self):
        self.add_example_requests()

        found = FriendRepository.get_request_between_users(self.klara.id, self.litong.id)

        self.assertEqual(found.id, self.klara_to_litong.id)

    def test_finds_the_request_when_the_recipient_is_given_first(self):
        # Klara sent it to Litong, but we ask with Litong first:
        # the order of the two users mustn't matter.
        self.add_example_requests()

        found = FriendRepository.get_request_between_users(self.litong.id, self.klara.id)

        self.assertEqual(found.id, self.klara_to_litong.id)

    def test_finds_pending_requests_too(self):
        # The service needs to see pending requests, to say "Request already sent".
        self.add_example_requests()

        found = FriendRepository.get_request_between_users(self.klara.id, self.timu.id)

        self.assertEqual(found.status, "pending")

    def test_returns_none_when_there_is_no_request(self):
        self.add_example_requests()

        found = FriendRepository.get_request_between_users(self.klara.id, self.noku.id)

        self.assertIsNone(found)
    
    # --- get_friend_ids ---

    def test_friend_ids_include_both_directions(self):
        # Klara asked Litong, and Ahmed asked Klara: both are her friends.
        self.add_example_requests()

        friend_ids = FriendRepository.get_friend_ids(self.klara.id)

        # assertCountEqual = same items, ANY order. A query without ORDER BY
        # doesn't promise an order, so assertEqual([...]) could fail at random.
        self.assertCountEqual(friend_ids, [self.litong.id, self.ahmed.id])

    def test_friend_ids_leave_out_pending_requests_and_strangers(self):
        self.add_example_requests()

        friend_ids = FriendRepository.get_friend_ids(self.klara.id)

        self.assertNotIn(self.timu.id, friend_ids)   # pending, not accepted yet
        self.assertNotIn(self.noku.id, friend_ids)  # no request at all
        self.assertNotIn(self.klara.id, friend_ids) # never yourself

    def test_friendship_works_from_both_sides(self):
        # Klara is in Litong's list too, not only the other way round.
        self.add_example_requests()

        self.assertEqual(FriendRepository.get_friend_ids(self.litong.id), [self.klara.id])

    def test_no_friends_gives_an_empty_list(self):
        # [] rather than None, so the leaderboard can always do [me.id] + friend_ids.
        self.assertEqual(FriendRepository.get_friend_ids(self.noku.id), [])

    # --- the table's rules (models.py) ---

    def test_new_request_is_pending_with_a_created_time(self):
        request = self.add_request(self.klara, self.litong)

        self.assertEqual(request.status, "pending")    # the column default
        self.assertIsNotNone(request.created_at)        # default=app_now ran
        self.assertIsNone(request.responded_at)         # not accepted yet

    def test_cannot_send_a_request_to_yourself(self):
        # ck_friend_requests_not_yourself: from_user_id <> to_user_id
        db.session.add(FriendRequest(from_user_id=self.klara.id, to_user_id=self.klara.id))

        # The error happens when the row is actually sent to the database,
        # which is at commit(), so the commit goes inside the "with".
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_cannot_send_the_same_request_twice(self):
        # uq_friend_requests_pair: at most one Klara → Litong row.
        self.add_request(self.klara, self.litong)
        db.session.add(FriendRequest(from_user_id=self.klara.id, to_user_id=self.litong.id))

        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_status_must_be_pending_or_accepted(self):
        # ck_friend_requests_status
        db.session.add(
            FriendRequest(from_user_id=self.klara.id, to_user_id=self.litong.id, status="declined")
        )

        with self.assertRaises(IntegrityError):
            db.session.commit()
    
    # --- send_friend_request ---

    def test_send_by_username_creates_a_pending_request(self):
        message = send_friend_request(self.klara, "litong", NOW)

        request = FriendRepository.get_request_between_users(self.klara.id, self.litong.id)
        self.assertEqual(message, "Request sent to litong.")
        self.assertEqual(request.from_user_id, self.klara.id)   # Klara is the sender
        self.assertEqual(request.to_user_id, self.litong.id)
        self.assertEqual(request.status, "pending")
        self.assertEqual(request.created_at, NOW)               # the time we passed in

    def test_send_by_email(self):
        send_friend_request(self.klara, "litong@example.com", NOW)

        self.assertIsNotNone(
            FriendRepository.get_request_between_users(self.klara.id, self.litong.id)
        )

    def test_send_ignores_spaces_and_capitals(self):
        # People type "  Litong " or "Litong@Example.com"; both should still work.
        send_friend_request(self.klara, "  Litong ", NOW)
        send_friend_request(self.klara, "Ahmed@Example.com", NOW)

        self.assertIsNotNone(
            FriendRepository.get_request_between_users(self.klara.id, self.litong.id)
        )
        self.assertIsNotNone(
            FriendRepository.get_request_between_users(self.klara.id, self.ahmed.id)
        )

    def test_send_to_an_unknown_user_fails_and_saves_nothing(self):
        # assertRaisesRegex checks the error type AND that the message contains this text.
        with self.assertRaisesRegex(ValueError, "No rat with that username or email"):
            send_friend_request(self.klara, "nobody", NOW)

        self.assertEqual(FriendRequest.query.count(), 0)

    def test_cannot_add_yourself(self):
        with self.assertRaisesRegex(ValueError, "You can't add yourself"):
            send_friend_request(self.klara, "klara", NOW)

        self.assertEqual(FriendRequest.query.count(), 0)

    def test_user_without_a_username_is_not_found(self):
        # Signed up, but hasn't named their rat yet, so they can't be on the leaderboard.
        nameless = User(email="nameless@example.com", password_hash="not-a-real-hash")
        db.session.add(nameless)
        db.session.commit()

        with self.assertRaisesRegex(ValueError, "No rat with that username or email"):
            send_friend_request(self.klara, "nameless@example.com", NOW)

    def test_cannot_send_the_same_request_twice(self):
        send_friend_request(self.klara, "litong", NOW)

        with self.assertRaisesRegex(ValueError, "already sent"):
            send_friend_request(self.klara, "litong", NOW)

        self.assertEqual(FriendRequest.query.count(), 1)

    def test_cannot_send_a_request_to_a_friend(self):
        self.add_request(self.klara, self.litong, "accepted")

        with self.assertRaisesRegex(ValueError, "already friends"):
            send_friend_request(self.klara, "litong", NOW)

    def test_sending_to_someone_who_already_asked_you_makes_you_friends(self):
        # Ahmed asked Klara. Klara doesn't see it and types "ahmed" herself.
        self.add_request(self.ahmed, self.klara, "pending")

        message = send_friend_request(self.klara, "ahmed", NOW)

        request = FriendRepository.get_request_between_users(self.klara.id, self.ahmed.id)
        self.assertEqual(message, "You're now friends with ahmed!")
        self.assertEqual(request.status, "accepted")
        self.assertEqual(request.responded_at, NOW)
        # Still ONE row: Ahmed's request was accepted, no second one was created.
        self.assertEqual(FriendRequest.query.count(), 1)

        # --- accept_request ---

    def test_the_recipient_can_accept(self):
        request = self.add_request(self.litong, self.klara)   # Litong asked Klara

        accept_request(self.klara, request.id, NOW)

        self.assertEqual(request.status, "accepted")
        self.assertEqual(request.responded_at, NOW)
        self.assertEqual(FriendRepository.get_friend_ids(self.klara.id), [self.litong.id])

    def test_the_sender_cannot_accept_their_own_request(self):
        # Otherwise anyone could make anyone their friend.
        request = self.add_request(self.klara, self.litong)

        with self.assertRaises(NotFoundError):
            accept_request(self.klara, request.id, NOW)

        self.assertEqual(request.status, "pending")

    def test_a_stranger_cannot_accept(self):
        request = self.add_request(self.klara, self.litong)

        with self.assertRaises(NotFoundError):
            accept_request(self.noku, request.id, NOW)

    def test_accepting_a_request_that_does_not_exist(self):
        with self.assertRaises(NotFoundError):
            accept_request(self.klara, 999, NOW)

    def test_cannot_accept_twice(self):
        request = self.add_request(self.litong, self.klara, "accepted")

        with self.assertRaises(NotFoundError):
            accept_request(self.klara, request.id, NOW)

    # --- cancel_or_decline_request ---

    def test_the_sender_can_cancel(self):
        request = self.add_request(self.klara, self.litong)
        # Save the id BEFORE deleting: afterwards the object is gone,
        # and reading request.id would raise an error.
        request_id = request.id

        cancel_or_decline_request(self.klara, request_id)

        self.assertIsNone(FriendRepository.get_request(request_id))

    def test_the_recipient_can_decline(self):
        request = self.add_request(self.klara, self.litong)
        request_id = request.id

        cancel_or_decline_request(self.litong, request_id)

        self.assertIsNone(FriendRepository.get_request(request_id))

    def test_a_stranger_cannot_cancel_or_decline(self):
        request = self.add_request(self.klara, self.litong)
        request_id = request.id

        with self.assertRaises(NotFoundError):
            cancel_or_decline_request(self.noku, request_id)

        self.assertIsNotNone(FriendRepository.get_request(request_id))   # still there

    def test_declining_does_not_remove_a_friendship(self):
        # An accepted request is a friendship, so it's removed with remove_friend, not here.
        request = self.add_request(self.klara, self.litong, "accepted")

        with self.assertRaises(NotFoundError):
            cancel_or_decline_request(self.litong, request.id)

    def test_after_declining_you_can_be_asked_again(self):
        # There's no "declined" status left behind, so a new request works.
        request = self.add_request(self.klara, self.litong)
        cancel_or_decline_request(self.litong, request.id)

        send_friend_request(self.klara, "litong", NOW)

        self.assertEqual(FriendRequest.query.count(), 1)
    
    # --- remove_friend ---

    def test_either_friend_can_remove_the_other(self):
        # Klara asked, Litong accepted, and now LITONG removes Klara:
        # it must work from the side that didn't send the request too.
        self.add_request(self.klara, self.litong, "accepted")

        remove_friend(self.litong, self.klara.id)

        self.assertEqual(FriendRepository.get_friend_ids(self.klara.id), [])
        self.assertEqual(FriendRepository.get_friend_ids(self.litong.id), [])

    def test_cannot_remove_someone_who_is_not_a_friend(self):
        with self.assertRaises(NotFoundError):
            remove_friend(self.klara, self.noku.id)

    def test_cannot_remove_a_pending_request_as_a_friend(self):
        # A pending request isn't a friendship yet: use cancel_or_decline_request.
        self.add_request(self.klara, self.litong)

        with self.assertRaises(NotFoundError):
            remove_friend(self.klara, self.litong.id)
            
if __name__ == "__main__":
    unittest.main()