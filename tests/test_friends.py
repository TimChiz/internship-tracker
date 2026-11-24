#Tests for the friend_requests table and FriendRepository
import unittest

from sqlalchemy.exc import IntegrityError

from app import create_app, db
from app.models import FriendRequest, User
from app.repositories.friends import FriendRepository

class FriendRepositoryTest(unittest.TestCase):
    """The friend_requests table rules and the two repository queries."""

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


if __name__ == "__main__":
    unittest.main()