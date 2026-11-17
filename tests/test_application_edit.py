"""Tests for the edit page, the delete confirmation and the status menu in each row (issue #40)."""

import unittest
from datetime import date

from flask_login import login_user

from app import create_app, db
from app.models import Application, User
from app.services.applications import (
    create_application,
    form_values_for,
    get_application,
    update_application,
    validate_application_form,
)
from app.services.auth import claim_username, register_user
from app.services.errors import NotFoundError


def form(**fields):
    """A valid edit form, with any fields replaced by the ones given."""
    values = {"company": "Stripe", "role": "SWE Intern", "status": "to_do"}
    values.update(fields)
    return values


class EditTestCase(unittest.TestCase):
    """Builds a test app with an empty database, two users, and one application owned by the first user."""

    def setUp(self):
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

        self.application = self.add_for(self.user, form(notes="Ask Sam"))
        self.edit_url = f"/applications/{self.application.id}/edit"
        self.delete_url = f"/applications/{self.application.id}/delete"

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.context.pop()

    def add_for(self, user, submitted):
        """Save an application for a user from a submitted form."""
        values, errors = validate_application_form(submitted)
        self.assertEqual(errors, {})
        return create_application(user, values)

    def update(self, **fields):
        """Save an edit of the test application from a submitted form."""
        values, errors = validate_application_form(form(**fields))
        self.assertEqual(errors, {})
        return update_application(self.user, self.application.id, values)

    def log_in(self):
        """Log the first user in. Flask-Login remembers the user for the rest of the test."""
        self.client.get(f"/test-only-login/{self.user.id}")


class UpdateApplicationTest(EditTestCase):
    """Checks the service that saves the edit page."""

    def test_saves_every_field(self):
        updated = self.update(
            company="Google", role="STEP Intern", url="https://google.com", status="in_progress",
            deadline="2026-12-01", is_rolling="on", notes="Referral from Sam",
        )

        self.assertEqual((updated.company, updated.role), ("Google", "STEP Intern"))
        self.assertEqual(updated.url, "https://google.com")
        self.assertEqual(updated.status, "in_progress")
        self.assertEqual(updated.deadline, date(2026, 12, 1))
        self.assertTrue(updated.is_rolling)
        self.assertEqual(updated.notes, "Referral from Sam")

    def test_moving_out_of_to_apply_sets_applied_at_once(self):
        """applied_at is set the first time it leaves To apply, and later edits never clear or move it."""
        self.assertIsNone(self.application.applied_at)

        first_sent = self.update(status="applied").applied_at
        self.assertIsNotNone(first_sent)

        self.assertEqual(self.update(status="to_do").applied_at, first_sent)
        self.assertEqual(self.update(status="interviewing").applied_at, first_sent)

    def test_cannot_update_someone_elses_application(self):
        values, _ = validate_application_form(form(company="Hacked"))

        with self.assertRaises(NotFoundError):
            update_application(self.other_user, self.application.id, values)
        self.assertEqual(self.application.company, "Stripe")

    def test_get_application_hides_other_users_and_missing_ones(self):
        with self.assertRaises(NotFoundError):
            get_application(self.other_user, self.application.id)
        with self.assertRaises(NotFoundError):
            get_application(self.user, 9999)


class FormValuesForTest(EditTestCase):
    """Checks that a saved application turns back into what the form fields expect."""

    def test_fills_in_every_field(self):
        saved = self.update(url="https://stripe.com", deadline="2026-12-01", is_rolling="on")

        self.assertEqual(form_values_for(saved), {
            "company": "Stripe",
            "role": "SWE Intern",
            "url": "https://stripe.com",
            "status": "to_do",
            "deadline": "2026-12-01",
            "notes": "",
            "is_rolling": "on",
        })

    def test_blank_optional_fields(self):
        values = form_values_for(self.application)

        self.assertEqual((values["url"], values["deadline"]), ("", ""))
        self.assertNotIn("is_rolling", values)


class EditPageTest(EditTestCase):
    """Checks /applications/<id>/edit."""

    def test_table_names_link_to_the_edit_page(self):
        self.log_in()
        html = self.client.get("/applications").get_data(as_text=True)

        self.assertIn(f'href="{self.edit_url}">Stripe - SWE Intern</a>', html)

    def test_shows_the_saved_application(self):
        self.update(deadline="2026-12-01", notes="Ask Sam")
        self.log_in()
        response = self.client.get(self.edit_url)
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('value="Stripe"', html)
        self.assertIn('value="2026-12-01"', html)
        self.assertIn('<option value="to_do" selected>', html)
        self.assertIn(">Ask Sam</textarea>", html)
        self.assertIn(f'href="{self.delete_url}"', html)

    def test_saving_goes_back_to_the_table(self):
        self.log_in()
        response = self.client.post(self.edit_url, data=form(company="Google", status="applied"))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith("/applications"))
        self.assertEqual(self.application.company, "Google")
        self.assertIsNotNone(self.application.applied_at)

    def test_bad_input_shows_errors_and_keeps_what_was_typed(self):
        self.log_in()
        response = self.client.post(self.edit_url, data=form(company="", role="Analyst"))
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 400)
        self.assertIn("Add a company.", html)
        self.assertIn('value="Analyst"', html)
        self.assertEqual((self.application.company, self.application.role), ("Stripe", "SWE Intern"))

    def test_someone_elses_or_missing_application_is_not_found(self):
        self.log_in()
        other = self.add_for(self.other_user, form(company="Secret Co"))

        self.assertEqual(self.client.get(f"/applications/{other.id}/edit").status_code, 404)
        self.assertEqual(self.client.post(f"/applications/{other.id}/edit", data=form()).status_code, 404)
        self.assertEqual(self.client.get("/applications/9999/edit").status_code, 404)
        self.assertEqual(other.company, "Secret Co")

    def test_logged_out_goes_to_login(self):
        response = self.client.get(self.edit_url)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith("/login"))


class StatusMenuTest(EditTestCase):
    """Checks the status menu in each table row and /applications/<id>/status."""

    def setUp(self):
        super().setUp()
        self.status_url = f"/applications/{self.application.id}/status"

    def test_each_row_has_a_status_menu(self):
        self.log_in()
        html = self.client.get("/applications").get_data(as_text=True)

        self.assertIn(f'action="{self.status_url}"', html)
        self.assertIn('name="status" value="applied"', html)
        # The current status is in the list but can't be picked again
        self.assertRegex(html, r'value="to_do" class="tag tag-to_do"\s+disabled')

    def test_picking_a_status_saves_it_and_goes_back_to_the_table(self):
        self.log_in()
        response = self.client.post(self.status_url, data={"status": "applied"})

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith("/applications"))
        self.assertEqual(self.application.status, "applied")
        self.assertIsNotNone(self.application.applied_at)

    def test_made_up_status_is_rejected(self):
        self.log_in()
        response = self.client.post(self.status_url, data={"status": "ghosted"})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.application.status, "to_do")

    def test_cannot_change_someone_elses_status(self):
        self.log_in()
        other = self.add_for(self.other_user, form(company="Secret Co"))

        response = self.client.post(f"/applications/{other.id}/status", data={"status": "rejected"})

        self.assertEqual(response.status_code, 404)
        self.assertEqual(other.status, "to_do")


class DeleteConfirmationTest(EditTestCase):
    """Checks /applications/<id>/delete."""

    def test_asks_before_deleting(self):
        self.log_in()
        response = self.client.get(self.delete_url)
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Delete Stripe - SWE Intern?", html)
        self.assertIn(f'href="{self.edit_url}"', html)
        self.assertIsNotNone(db.session.get(Application, self.application.id))

    def test_confirming_deletes_and_goes_back_to_the_table(self):
        self.log_in()
        response = self.client.post(self.delete_url)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith("/applications"))
        self.assertIsNone(db.session.get(Application, self.application.id))

    def test_cannot_delete_someone_elses_application(self):
        self.log_in()
        other = self.add_for(self.other_user, form(company="Secret Co"))

        self.assertEqual(self.client.get(f"/applications/{other.id}/delete").status_code, 404)
        self.assertEqual(self.client.post(f"/applications/{other.id}/delete").status_code, 404)
        self.assertIsNotNone(db.session.get(Application, other.id))


if __name__ == "__main__":
    unittest.main()
