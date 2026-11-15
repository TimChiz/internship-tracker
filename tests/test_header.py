"""Tests for the shared header on logged-in pages (issue #39): the sent count beside the rat,
and the racing rat that plays once when an application is marked as sent.

Run all tests from the repo root with `python3 -m unittest discover tests`.
"""

import unittest
from datetime import datetime

from flask_login import login_user

from app import create_app, db
from app.models import Application, User
from app.routes.applications import RACE_SESSION_KEY
from app.services.auth import claim_username, register_user
from app.services.header import DEFAULT_RAT_IMAGE, get_header_data, starts_race
from app.services.stats import count_sent, was_sent

SENT = datetime(2026, 11, 1)  # any time works; only "has it been sent" matters
LONG_AGO = datetime(2025, 1, 1)  # far outside this week, so a weekly count would miss it
RACING = "race-track is-racing"  # the race track's classes while the rat races


def sent_count_text(count):
    """The header's count as it appears in the page's HTML, e.g. "Applications sent: </span>4"."""
    return f"Applications sent: </span>{count}"


class HeaderTestCase(unittest.TestCase):
    """Builds a test app with an empty database and two named users. Nobody is logged in until log_in()."""

    def setUp(self):
        """Build the app, the database and the two users."""
        self.app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://"})

        @self.app.route("/test-only-login/<int:user_id>")
        def test_only_login(user_id):
            login_user(db.session.get(User, user_id))
            return "logged in"

        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        self.client = self.app.test_client()

        self.user = register_user("rat@example.com", "cheese123")
        claim_username(self.user, "rat_one")
        self.other_user = register_user("other@example.com", "cheese123")
        claim_username(self.other_user, "rat_two")

    def tearDown(self):
        """Throw the database away."""
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.context.pop()

    def save(self, user, status, applied_at=None):
        """Save an application for a user straight to the database. Pass applied_at for one that's been sent."""
        application = Application(user_id=user.id, company="Stripe", role="SWE Intern", status=status, applied_at=applied_at)
        db.session.add(application)
        db.session.commit()
        return application

    def log_in(self):
        """Log the first user in. Flask-Login remembers the user for the rest of the test."""
        self.client.get(f"/test-only-login/{self.user.id}")

    def change_status(self, application, status):
        """Pick a status from the application's status menu, like clicking it in the table."""
        return self.client.post(f"/applications/{application.id}/status", data={"status": status})

    def table(self):
        """Open the Applications table and return its HTML."""
        return self.client.get("/applications").get_data(as_text=True)


class WasSentTest(unittest.TestCase):
    """was_sent says whether an application has left To apply, whatever its status is now."""

    def test_not_sent_while_in_to_apply(self):
        """To-do and In progress haven't been sent."""
        for status in ("to_do", "in_progress"):
            with self.subTest(status=status):
                self.assertFalse(was_sent(Application(status=status)))

    def test_still_sent_after_an_offer_or_rejection(self):
        """Once sent, an application stays sent, even when it's closed."""
        for status in ("applied", "interviewing", "offer", "rejected"):
            with self.subTest(status=status):
                self.assertTrue(was_sent(Application(status=status, applied_at=SENT)))


class CountSentTest(HeaderTestCase):
    """count_sent counts every application the user has ever sent."""

    def test_counts_offers_and_rejections_but_not_to_apply(self):
        """Applied, Interviewing, Offer and Rejected count. To-do and In progress don't."""
        self.save(self.user, "to_do")
        self.save(self.user, "in_progress")
        self.save(self.user, "applied", SENT)
        self.save(self.user, "interviewing", SENT)
        self.save(self.user, "offer", SENT)
        self.save(self.user, "rejected", SENT)

        self.assertEqual(count_sent(self.user), 4)

    def test_counts_applications_sent_long_ago(self):
        """The count is all-time, not just this week."""
        self.save(self.user, "applied", LONG_AGO)

        self.assertEqual(count_sent(self.user), 1)

    def test_other_users_applications_dont_count(self):
        """Another user's sent applications don't change your count."""
        self.save(self.user, "applied", SENT)
        self.save(self.other_user, "applied", SENT)
        self.save(self.other_user, "offer", SENT)

        self.assertEqual(count_sent(self.user), 1)
        self.assertEqual(count_sent(self.other_user), 2)


class GetHeaderDataTest(HeaderTestCase):
    """get_header_data gathers the name, the rat picture and the count for the header."""

    def test_has_name_rat_and_count(self):
        """The header gets the username, the rat picture and the sent count."""
        self.save(self.user, "applied", SENT)
        self.save(self.user, "to_do")

        header = get_header_data(self.user)

        self.assertEqual(header.username, "rat_one")
        self.assertEqual(header.rat_image, DEFAULT_RAT_IMAGE)
        self.assertEqual(header.sent_count, 1)


class StartsRaceTest(unittest.TestCase):
    """starts_race says yes only when a save marks the application as sent for the first time."""

    def test_races_when_first_sent(self):
        """Leaving To apply for the first time races."""
        self.assertTrue(starts_race(False, Application(status="applied", applied_at=SENT)))

    def test_no_race_while_still_in_to_apply(self):
        """Saving an application that's still To-do or In progress doesn't race."""
        self.assertFalse(starts_race(False, Application(status="in_progress")))

    def test_no_race_when_it_was_sent_before(self):
        """Later changes to a sent application, like Applied to Interviewing, don't race again."""
        self.assertFalse(starts_race(True, Application(status="interviewing", applied_at=SENT)))


class RaceOnPageTest(HeaderTestCase):
    """The race plays on the next page after an application is first sent, and only once."""

    def setUp(self):
        """Start logged in."""
        super().setUp()
        self.log_in()

    def test_first_applied_races_once(self):
        """Marking an application as Applied races on the next page. Reloading doesn't race again."""
        application = self.save(self.user, "in_progress")
        self.change_status(application, "applied")

        first = self.table()
        reload = self.table()

        self.assertIn(RACING, first)
        self.assertIn(sent_count_text(1), first)
        self.assertNotIn(RACING, reload)

    def test_race_flag_is_saved_then_used_up(self):
        """The save puts the flag in the session, and the next page takes it out."""
        application = self.save(self.user, "to_do")
        self.change_status(application, "applied")
        with self.client.session_transaction() as session:
            self.assertTrue(session[RACE_SESSION_KEY])

        self.table()
        with self.client.session_transaction() as session:
            self.assertNotIn(RACE_SESSION_KEY, session)

    def test_later_status_changes_dont_race(self):
        """Applied to Interviewing doesn't race, and neither does an offer or a rejection."""
        for before, after in (("applied", "interviewing"), ("interviewing", "offer"), ("interviewing", "rejected")):
            with self.subTest(before=before, after=after):
                application = self.save(self.user, before, SENT)
                self.change_status(application, after)

                self.assertNotIn(RACING, self.table())

    def test_sending_again_after_moving_back_doesnt_race(self):
        """Applied, back to To-do, then Applied again races only the first time."""
        application = self.save(self.user, "to_do")
        self.change_status(application, "applied")
        self.table()  # the first race plays here

        self.change_status(application, "to_do")
        self.change_status(application, "applied")
        html = self.table()

        self.assertNotIn(RACING, html)
        self.assertIn(sent_count_text(1), html)

    def test_adding_as_applied_races(self):
        """Adding an application that's already Applied, from the Add popup, races."""
        self.client.post("/applications/new", data={"company": "Stripe", "role": "SWE Intern", "status": "applied"})

        html = self.table()

        self.assertIn(RACING, html)
        self.assertIn(sent_count_text(1), html)

    def test_adding_to_apply_doesnt_race(self):
        """Adding a To-do application doesn't race or change the count."""
        self.client.post("/applications/new", data={"company": "Stripe", "role": "SWE Intern", "status": "to_do"})

        html = self.table()

        self.assertNotIn(RACING, html)
        self.assertIn(sent_count_text(0), html)

    def test_add_with_errors_doesnt_race(self):
        """An Add that fails (no company here) saves nothing, so nothing races."""
        response = self.client.post("/applications/new", data={"company": "", "role": "SWE Intern", "status": "applied"})

        self.assertEqual(response.status_code, 400)
        self.assertNotIn(RACING, response.get_data(as_text=True))
        self.assertNotIn(RACING, self.table())

    def test_first_send_from_the_edit_page_races(self):
        """Saving the edit page with a sent status for the first time races."""
        application = self.save(self.user, "to_do")
        self.client.post(f"/applications/{application.id}/edit",
                         data={"company": "Stripe", "role": "SWE Intern", "status": "applied"})

        self.assertIn(RACING, self.table())


class HeaderOnPageTest(HeaderTestCase):
    """Every logged-in Applications page shows the header with the user's own details."""

    def setUp(self):
        """Start logged in."""
        super().setUp()
        self.log_in()

    def test_table_shows_the_header(self):
        """The table has the header with the name, count, Log out and day/night switch, and a resting race track."""
        self.save(self.user, "applied", SENT)
        self.save(self.other_user, "applied", SENT)  # shouldn't change the count

        html = self.table()

        self.assertIn('class="app-header"', html)
        self.assertIn(">rat_one</p>", html)
        self.assertIn(sent_count_text(1), html)
        self.assertIn("Log out</button>", html)
        self.assertIn('id="theme-toggle"', html)
        self.assertIn('class="race-track"', html)  # resting, not racing

    def test_edit_and_delete_pages_show_the_header(self):
        """The edit page and the delete confirmation have the same header."""
        application = self.save(self.user, "to_do")
        for page in ("edit", "delete"):
            with self.subTest(page=page):
                html = self.client.get(f"/applications/{application.id}/{page}").get_data(as_text=True)

                self.assertIn('class="app-header"', html)
                self.assertIn(">rat_one</p>", html)

    def test_long_names_get_smaller_type(self):
        """Names over 10 characters get the smaller type, so they stay on one line."""
        self.user.username = "a_very_long_rat"
        db.session.commit()

        self.assertIn("app-header-name is-long", self.table())


if __name__ == "__main__":
    unittest.main()
