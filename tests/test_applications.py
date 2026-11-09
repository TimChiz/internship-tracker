"""Tests for the Applications page (issue #29): the Add form rules, grouping and sorting,
and the /applications routes."""

import unittest
from datetime import date, datetime

from flask_login import login_user

from app import create_app, db
from app.models import Application, User
from app.services.applications import (
    build_row,
    create_application,
    group_applications,
    validate_application_form,
)
from app.services.auth import claim_username, register_user

TODAY = date(2026, 11, 9)


def make_application(**fields):
    """An unsaved Application with sensible defaults, for the sorting tests."""
    defaults = {
        "company": "Stripe",
        "role": "SWE Intern",
        "status": "to_do",
        "is_rolling": False,
        "notes": "",
        "created_at": datetime(2026, 11, 1),
        "updated_at": datetime(2026, 11, 1),
    }
    defaults.update(fields)
    return Application(**defaults)


def row_names(section):
    """The company of each row in a section, in order."""
    return [row["name"].split(" - ")[0] for row in section["rows"]]


class ValidateApplicationFormTest(unittest.TestCase):
    """Checks the rules for the Add popup."""

    def test_valid_form_gives_clean_values(self):
        values, errors = validate_application_form({
            "company": "  Stripe ",
            "role": "SWE Intern",
            "url": "https://stripe.com/jobs",
            "status": "in_progress",
            "deadline": "2026-11-20",
            "is_rolling": "on",
            "notes": " Ask Sam ",
        })

        self.assertEqual(errors, {})
        self.assertEqual(values["company"], "Stripe")
        self.assertEqual(values["deadline"], date(2026, 11, 20))
        self.assertTrue(values["is_rolling"])
        self.assertEqual(values["notes"], "Ask Sam")

    def test_optional_fields_can_be_empty(self):
        values, errors = validate_application_form({"company": "Stripe", "role": "SWE Intern"})

        self.assertEqual(errors, {})
        self.assertIsNone(values["url"])
        self.assertIsNone(values["deadline"])
        self.assertFalse(values["is_rolling"])
        self.assertEqual(values["status"], "to_do")

    def test_company_and_role_are_required(self):
        _, errors = validate_application_form({"company": "   ", "role": ""})

        self.assertEqual(errors["company"], "Add a company.")
        self.assertEqual(errors["role"], "Add a role.")

    def test_company_and_role_have_a_length_limit(self):
        _, errors = validate_application_form({"company": "S" * 121, "role": "R" * 121})

        self.assertIn("company", errors)
        self.assertIn("role", errors)

    def test_link_must_be_a_web_address(self):
        _, errors = validate_application_form(
            {"company": "Stripe", "role": "SWE Intern", "url": "javascript:alert(1)"}
        )

        self.assertIn("url", errors)

    def test_rejects_unknown_status_and_bad_date(self):
        _, errors = validate_application_form({
            "company": "Stripe", "role": "SWE Intern", "status": "ghosted", "deadline": "next week",
        })

        self.assertIn("status", errors)
        self.assertIn("deadline", errors)


class GroupApplicationsTest(unittest.TestCase):
    """Checks which section each application lands in, and the order inside each section."""

    def test_sections_come_in_order_with_their_statuses(self):
        sections = group_applications([
            make_application(company="A", status="to_do"),
            make_application(company="B", status="interviewing"),
            make_application(company="C", status="rejected"),
        ], TODAY)

        self.assertEqual([s["id"] for s in sections], ["to_apply", "applied", "closed"])
        self.assertEqual([row_names(s) for s in sections], [["A"], ["B"], ["C"]])

    def test_to_apply_puts_most_urgent_first(self):
        sections = group_applications([
            make_application(company="NoDeadline"),
            make_application(company="Overdue", deadline=date(2026, 11, 1)),
            make_application(company="Later", deadline=date(2026, 11, 30)),
            make_application(company="Rolling", is_rolling=True),
            make_application(company="Soon", deadline=date(2026, 11, 10)),
        ], TODAY)

        self.assertEqual(row_names(sections[0]), ["Soon", "Later", "Rolling", "NoDeadline", "Overdue"])

    def test_ties_go_oldest_added_first(self):
        sections = group_applications([
            make_application(company="Newer", deadline=date(2026, 11, 20), created_at=datetime(2026, 11, 5)),
            make_application(company="Older", deadline=date(2026, 11, 20), created_at=datetime(2026, 11, 2)),
        ], TODAY)

        self.assertEqual(row_names(sections[0]), ["Older", "Newer"])

    def test_applied_is_most_recently_applied_first(self):
        sections = group_applications([
            make_application(company="First", status="applied", applied_at=datetime(2026, 11, 1)),
            make_application(company="Latest", status="interviewing", applied_at=datetime(2026, 11, 8)),
        ], TODAY)

        self.assertEqual(row_names(sections[1]), ["Latest", "First"])

    def test_closed_is_most_recently_updated_first(self):
        sections = group_applications([
            make_application(company="Old", status="offer", updated_at=datetime(2026, 10, 1)),
            make_application(company="Recent", status="rejected", updated_at=datetime(2026, 11, 8)),
        ], TODAY)

        self.assertEqual(row_names(sections[2]), ["Recent", "Old"])


class BuildRowTest(unittest.TestCase):
    """Checks what each row shows in the Deadline column."""

    def test_due_tomorrow_is_urgent(self):
        row = build_row(make_application(deadline=date(2026, 11, 10)), TODAY)

        self.assertEqual(row["deadline_text"], "Nov 10, 2026")
        self.assertEqual((row["label"], row["urgency"]), ("Due tomorrow", "urgent"))

    def test_rolling_shows_once(self):
        row = build_row(make_application(is_rolling=True), TODAY)

        self.assertEqual(row["deadline_text"], "Rolling")
        self.assertIsNone(row["label"])

    def test_missing_deadline(self):
        row = build_row(make_application(), TODAY)

        self.assertEqual(row["deadline_text"], "No deadline")

    def test_applied_rows_have_no_countdown(self):
        row = build_row(make_application(status="applied", deadline=date(2026, 11, 10)), TODAY)

        self.assertIsNone(row["label"])

    def test_name_and_status_label(self):
        row = build_row(make_application(), TODAY)

        self.assertEqual(row["name"], "Stripe - SWE Intern")
        self.assertEqual(row["status_label"], "To-do")


class ApplicationsPageTest(unittest.TestCase):
    """Checks the /applications routes with a real (in-memory) database."""

    def setUp(self):
        """Build a test app with an empty database, a user with a username, and a test-only login route."""
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

    def log_in(self):
        """Log the test user in. Flask-Login remembers the user for the rest of the test."""
        self.client.get(f"/test-only-login/{self.user.id}")

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.context.pop()

    def add(self, **fields):
        """Log in, submit the Add popup and return the response."""
        self.log_in()
        form = {"company": "Stripe", "role": "SWE Intern", "status": "to_do"}
        form.update(fields)
        return self.client.post("/applications/new", data=form)

    def test_logged_out_goes_to_login(self):
        response = self.client.get("/applications")

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith("/login"))

    def test_empty_state(self):
        self.log_in()
        html = self.client.get("/applications").get_data(as_text=True)

        self.assertIn("No applications yet", html)
        self.assertIn('popovertarget="add-popup"', html)
        self.assertNotIn('class="app-table"', html)

    def test_adding_shows_the_row_in_to_apply(self):
        response = self.add(deadline="2026-12-01", notes="Ask Sam")

        self.assertEqual(response.status_code, 302)
        html = self.client.get("/applications").get_data(as_text=True)
        self.assertIn("Stripe - SWE Intern", html)
        self.assertIn("To apply · 1", html)
        self.assertIn("Applied · 0", html)
        self.assertIn("Ask Sam", html)
        self.assertNotIn("No applications yet", html)

    def test_adding_as_applied_records_when(self):
        self.add(status="applied")

        application = db.session.scalar(db.select(Application))
        self.assertIsNotNone(application.applied_at)
        self.assertIn("Applied · 1", self.client.get("/applications").get_data(as_text=True))

    def test_bad_input_reopens_the_popup_with_what_was_typed(self):
        response = self.add(company="", role="Analyst")
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 400)
        self.assertIn('class="popup is-open"', html)
        self.assertIn("Add a company.", html)
        self.assertIn('value="Analyst"', html)
        self.assertEqual(db.session.scalar(db.select(db.func.count(Application.id))), 0)

    def test_closed_applications_are_behind_see_more(self):
        self.add(status="rejected")
        html = self.client.get("/applications").get_data(as_text=True)

        self.assertIn("<summary>See more (1)</summary>", html)

    def test_other_users_applications_are_not_shown(self):
        self.log_in()
        other = register_user("other@example.com", "cheese123")
        create_application(other, validate_application_form({"company": "Secret Co", "role": "Spy"})[0])

        html = self.client.get("/applications").get_data(as_text=True)
        self.assertNotIn("Secret Co", html)


if __name__ == "__main__":
    unittest.main()
