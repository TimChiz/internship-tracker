import unittest
from datetime import date, datetime

from app.constants import STATUS_OPTIONS, TO_APPLY_STATUSES
from app.services.deadlines import format_date, get_deadline_label, get_week_bounds


class DeadlineTests(unittest.TestCase):
    def test_week_bounds_start_monday_and_end_next_monday(self):
        start, end = get_week_bounds(date(2026, 10, 21))

        # The next Monday is the exclusive boundary, not part of this week.
        self.assertEqual(start, datetime(2026, 10, 19))
        self.assertEqual(end, datetime(2026, 10, 26))

    def test_week_bounds_when_today_is_monday(self):
        start, end = get_week_bounds(date(2026, 10, 19))

        self.assertEqual(start, datetime(2026, 10, 19))
        self.assertEqual(end, datetime(2026, 10, 26))

    def test_formats_date_without_platform_specific_day_directive(self):
        # Confirm the day has no leading zero, including on Windows.
        self.assertEqual(format_date(date(2026, 10, 19)), "Oct 19, 2026")

    def test_only_labels_applications_in_to_apply_statuses(self):
        # Exercise every configured status so section membership stays centralized.
        for status in STATUS_OPTIONS:
            with self.subTest(status=status):
                expected = (
                    ("Rolling", "normal")
                    if status in TO_APPLY_STATUSES
                    else (None, None)
                )
                self.assertEqual(
                    get_deadline_label(
                        None,
                        True,
                        status,
                        date(2026, 10, 19),
                    ),
                    expected,
                )

    def test_rolling_label_requires_to_apply_status(self):
        self.assertEqual(
            get_deadline_label(
                None, True, TO_APPLY_STATUSES[0], date(2026, 10, 19)
            ),
            ("Rolling", "normal"),
        )
        self.assertEqual(
            get_deadline_label(
                None, False, TO_APPLY_STATUSES[1], date(2026, 10, 19)
            ),
            (None, None),
        )

    def test_deadline_labels_and_urgency(self):
        today = date(2026, 10, 19)
        # Check both sides of each urgency threshold: past, today, tomorrow, 7/8 days.
        expected = (
            (date(2026, 10, 18), ("Deadline passed", "overdue")),
            (today, ("Due today", "urgent")),
            (date(2026, 10, 20), ("Due tomorrow", "urgent")),
            (date(2026, 10, 21), ("2 days left", "soon")),
            (date(2026, 10, 26), ("7 days left", "soon")),
            (date(2026, 10, 27), ("8 days left", "normal")),
        )

        for deadline, result in expected:
            with self.subTest(deadline=deadline):
                self.assertEqual(
                    get_deadline_label(
                        deadline, False, TO_APPLY_STATUSES[0], today
                    ),
                    result,
                )


if __name__ == "__main__":
    unittest.main()
