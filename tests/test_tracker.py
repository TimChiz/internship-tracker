"""Tests for quick-add parsing, display names and application status changes."""

import unittest
from datetime import datetime, timezone
from types import SimpleNamespace

from app import create_app, db
from app.constants import SECTIONS, STATUS_OPTIONS, TO_APPLY_STATUSES
from app.models import Application, User
from app.repositories.applications import ApplicationRepository
from app.services.errors import NotFoundError
from app.services.tracker import (
    QuickAddResult,
    change_application_status,
    create_application,
    delete_application,
    get_display_name,
    parse_quick_add,
    update_application_status,
)


class ParseQuickAddTest(unittest.TestCase):
    def test_parses_urls_without_fetching_them(self):
        result = parse_quick_add("  HTTPS://www.stripe.com/jobs  ")

        self.assertEqual(result, QuickAddResult(url="HTTPS://www.stripe.com/jobs"))
        self.assertEqual((result.company, result.role), ("", ""))

    def test_splits_company_and_role_on_supported_dashes(self):
        for separator in ("–", "—", "-"):
            with self.subTest(separator=separator):
                result = parse_quick_add(f"Stripe {separator} SWE Intern")

                self.assertEqual((result.company, result.role), ("Stripe", "SWE Intern"))
                self.assertEqual(result.url, "")

    def test_company_without_role(self):
        self.assertEqual(parse_quick_add(" Stripe "), QuickAddResult(company="Stripe"))

    def test_rejects_empty_input_with_user_message(self):
        with self.assertRaisesRegex(
            ValueError, "^Type a company and role, or paste a link\\.$"
        ):
            parse_quick_add("   ")

    def test_rejects_company_longer_than_120_characters(self):
        with self.assertRaisesRegex(ValueError, "Company must be 120 characters"):
            parse_quick_add("S" * 121)

    def test_rejects_role_longer_than_120_characters(self):
        with self.assertRaisesRegex(ValueError, "Role must be 120 characters"):
            parse_quick_add(f"Stripe - {'S' * 121}")


class GetDisplayNameTest(unittest.TestCase):
    def test_uses_company_and_role(self):
        self.assertEqual(
            get_display_name(" Stripe ", " SWE Intern ", ""),
            "Stripe - SWE Intern",
        )

    def test_uses_url_site_without_www(self):
        self.assertEqual(
            get_display_name("", "", "https://www.stripe.com/jobs"),
            "stripe.com",
        )

    def test_uses_untitled_when_all_fields_are_blank(self):
        self.assertEqual(get_display_name("", "", ""), "Untitled")


class ChangeApplicationStatusTest(unittest.TestCase):
    def test_records_first_time_leaving_to_apply_and_never_changes_it(self):
        to_apply_status = TO_APPLY_STATUSES[0]
        applied_status = next(
            section_statuses[0]
            for section_id, _, section_statuses in SECTIONS
            if section_id == "applied"
        )
        # Inject times to prove only the first move out of To apply is recorded.
        application = SimpleNamespace(status=to_apply_status, applied_at=None)
        first_time = datetime(2026, 11, 6, 12, 0, tzinfo=timezone.utc)
        later_time = datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc)

        change_application_status(application, applied_status, first_time)
        self.assertEqual(application.status, applied_status)
        self.assertEqual(application.applied_at, first_time)

        change_application_status(application, to_apply_status, later_time)
        self.assertEqual(application.status, to_apply_status)
        self.assertEqual(application.applied_at, first_time)

        change_application_status(application, applied_status, later_time)
        self.assertEqual(application.status, applied_status)
        self.assertEqual(application.applied_at, first_time)

    def test_rejects_status_outside_the_stored_status_values(self):
        application = SimpleNamespace(status=TO_APPLY_STATUSES[0], applied_at=None)

        with self.assertRaises(ValueError):
            change_application_status(application, "not-a-status", datetime.now(timezone.utc))

        self.assertIn(application.status, STATUS_OPTIONS)
        self.assertIsNone(application.applied_at)


class TrackerServiceTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app(
            {"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://"}
        )
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        self.user_a = User(email="a@example.com", password_hash="hash")
        self.user_b = User(email="b@example.com", password_hash="hash")
        db.session.add_all([self.user_a, self.user_b])
        db.session.commit()
        self.current_time = datetime(2026, 11, 10, 12, 0)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.context.pop()

    def test_creates_application_from_a_link(self):
        application = create_application(
            self.user_a.id, "https://www.stripe.com/jobs", self.current_time
        )

        self.assertEqual(application.url, "https://www.stripe.com/jobs")
        self.assertEqual((application.company, application.role), ("", ""))
        self.assertEqual(application.status, "to_do")
        self.assertEqual(application.created_at, self.current_time)
        self.assertEqual(application.updated_at, self.current_time)

    def test_creates_application_from_company_and_role(self):
        application = create_application(
            self.user_a.id, "Stripe – SWE Intern", self.current_time
        )

        self.assertEqual((application.company, application.role), ("Stripe", "SWE Intern"))
        self.assertIsNone(application.url)

    def test_blank_quick_add_fails_without_saving(self):
        with self.assertRaisesRegex(ValueError, "Type a company and role"):
            create_application(self.user_a.id, "  ", self.current_time)

        self.assertEqual(Application.query.count(), 0)

    def test_update_to_applied_records_sent_and_updated_times(self):
        application = create_application(
            self.user_a.id, "Stripe - SWE Intern", self.current_time
        )
        applied_time = datetime(2026, 11, 11, 12, 0)

        updated = update_application_status(
            self.user_a.id, application.id, "applied", applied_time
        )

        self.assertEqual(updated.status, "applied")
        self.assertEqual(updated.applied_at, applied_time)
        self.assertEqual(updated.updated_at, applied_time)

    def test_unknown_status_fails(self):
        application = create_application(
            self.user_a.id, "Stripe - SWE Intern", self.current_time
        )

        with self.assertRaises(ValueError):
            update_application_status(
                self.user_a.id, application.id, "made_up", self.current_time
            )

        db.session.refresh(application)
        self.assertEqual(application.status, "to_do")

    def test_another_user_cannot_update_or_delete_application(self):
        application = create_application(
            self.user_a.id, "Stripe - SWE Intern", self.current_time
        )

        with self.assertRaises(NotFoundError):
            update_application_status(
                self.user_b.id, application.id, "applied", self.current_time
            )
        with self.assertRaises(NotFoundError):
            delete_application(self.user_b.id, application.id)

        self.assertIsNotNone(
            ApplicationRepository.get_for_user(self.user_a.id, application.id)
        )

    def test_delete_removes_owned_application(self):
        application = create_application(
            self.user_a.id, "Stripe - SWE Intern", self.current_time
        )

        delete_application(self.user_a.id, application.id)

        self.assertIsNone(
            ApplicationRepository.get_for_user(self.user_a.id, application.id)
        )

    def test_sent_count_includes_start_but_excludes_end(self):
        start = datetime(2026, 11, 1)
        end = datetime(2026, 11, 8)
        at_start = create_application(self.user_a.id, "Start", start)
        at_end = create_application(self.user_a.id, "End", end)
        other_user_at_start = create_application(self.user_b.id, "Other user", start)
        at_start.applied_at = start
        at_end.applied_at = end
        other_user_at_start.applied_at = start
        db.session.commit()

        self.assertEqual(
            ApplicationRepository.count_sent_between(self.user_a.id, start, end), 1
        )


if __name__ == "__main__":
    unittest.main()
