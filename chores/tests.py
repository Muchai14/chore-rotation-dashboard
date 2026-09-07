from datetime import date

from django.test import SimpleTestCase

from chores.services import current_assignments, week_index

PEOPLE = ["Alex", "Sam", "Jordan", "Taylor"]
CHORES = ["Dishes", "Trash & Recycling", "Bathroom Cleaning", "Vacuuming & Sweeping", "Kitchen Counters"]
START = date(2026, 1, 5)  # a Monday


class WeekIndexTests(SimpleTestCase):
    def test_start_date_is_week_zero(self):
        self.assertEqual(week_index(START, START), 0)

    def test_stays_in_week_zero_until_seven_days_pass(self):
        self.assertEqual(week_index(START, date(2026, 1, 11)), 0)

    def test_advances_on_seventh_day(self):
        self.assertEqual(week_index(START, date(2026, 1, 12)), 1)

    def test_several_weeks_later(self):
        self.assertEqual(week_index(START, date(2026, 2, 16)), 6)

    def test_raises_if_today_before_start(self):
        with self.assertRaises(ValueError):
            week_index(START, date(2026, 1, 4))


class CurrentAssignmentsTests(SimpleTestCase):
    def test_week_zero_assigns_each_chore_its_own_offset_person(self):
        result = current_assignments(PEOPLE, CHORES, START, START)
        self.assertEqual(
            result,
            [
                ("Dishes", "Alex"),
                ("Trash & Recycling", "Sam"),
                ("Bathroom Cleaning", "Jordan"),
                ("Vacuuming & Sweeping", "Taylor"),
                ("Kitchen Counters", "Alex"),
            ],
        )

    def test_assignments_shift_by_one_person_next_week(self):
        result = current_assignments(PEOPLE, CHORES, START, date(2026, 1, 12))
        self.assertEqual(
            result,
            [
                ("Dishes", "Sam"),
                ("Trash & Recycling", "Jordan"),
                ("Bathroom Cleaning", "Taylor"),
                ("Vacuuming & Sweeping", "Alex"),
                ("Kitchen Counters", "Sam"),
            ],
        )

    def test_rotation_wraps_around_after_full_cycle(self):
        # 4 people, so week 4 should match week 0's assignments.
        week_0 = current_assignments(PEOPLE, CHORES, START, START)
        week_4 = current_assignments(PEOPLE, CHORES, START, date(2026, 2, 2))
        self.assertEqual(week_0, week_4)

    def test_different_chores_go_to_different_people_within_a_week(self):
        result = current_assignments(PEOPLE, CHORES[:4], START, date(2026, 1, 26))
        assigned_people = [person for _, person in result]
        self.assertEqual(len(assigned_people), len(set(assigned_people)))

    def test_raises_if_people_empty(self):
        with self.assertRaises(ValueError):
            current_assignments([], CHORES, START, START)
