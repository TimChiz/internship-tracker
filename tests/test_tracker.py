"""Tests for quick-add parsing, display names and application status changes."""

import unittest
from datetime import datetime, timezone
from types import SimpleNamespace

from app.constants import SECTIONS, STATUS_OPTIONS, TO_APPLY_STATUSES
from app.services.tracker import (
    QuickAddResult,
    change_application_status,
    get_display_name,
    parse_quick_add,
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


if __name__ == "__main__":
    unittest.main()
