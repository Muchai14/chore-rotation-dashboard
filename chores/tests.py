from datetime import date, timedelta

from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from chores.models import Chore, ChoreCompletion, Person
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


class DashboardViewTests(TestCase):
    def setUp(self):
        self.people = [
            Person.objects.create(name=name, order=i)
            for i, name in enumerate(PEOPLE, start=1)
        ]
        self.chores = [
            Chore.objects.create(name=name, order=i)
            for i, name in enumerate(CHORES, start=1)
        ]

    def test_empty_state_when_nothing_seeded(self):
        Person.objects.all().delete()
        Chore.objects.all().delete()

        response = self.client.get(reverse("dashboard"))

        self.assertIsNone(response.context["rows"])
        self.assertContains(response, "No people or chores configured yet")

    def test_shows_current_week_assignments_and_done_status(self):
        start = date.today() - timedelta(weeks=2)
        with override_settings(CHORE_ROTATION_START_DATE=start):
            done_chore = self.chores[0]
            ChoreCompletion.objects.create(chore=done_chore, week_index=2, done=True)

            response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.context["week_index"], 2)
        rows_by_chore = {row["chore"].name: row for row in response.context["rows"]}

        self.assertTrue(rows_by_chore[done_chore.name]["done"])
        other_chore_names = [c.name for c in self.chores if c != done_chore]
        for name in other_chore_names:
            self.assertFalse(rows_by_chore[name]["done"])

        expected_assignments = {
            chore.name: person.name
            for chore, person in current_assignments(self.people, self.chores, start, date.today())
        }
        for name, row in rows_by_chore.items():
            self.assertEqual(row["person"].name, expected_assignments[name])


class OverdueFlaggingTests(TestCase):
    def setUp(self):
        self.people = [
            Person.objects.create(name=name, order=i)
            for i, name in enumerate(PEOPLE, start=1)
        ]
        self.chores = [
            Chore.objects.create(name=name, order=i)
            for i, name in enumerate(CHORES, start=1)
        ]

    def test_week_zero_is_never_overdue(self):
        start = date.today()  # today falls in week 0; no previous week exists
        with override_settings(CHORE_ROTATION_START_DATE=start):
            response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.context["week_index"], 0)
        self.assertTrue(all(not row["overdue"] for row in response.context["rows"]))

    def test_overdue_when_previous_week_has_no_completion_record(self):
        start = date.today() - timedelta(weeks=1)
        with override_settings(CHORE_ROTATION_START_DATE=start):
            response = self.client.get(reverse("dashboard"))

        self.assertTrue(all(row["overdue"] for row in response.context["rows"]))

    def test_overdue_when_previous_week_marked_not_done(self):
        start = date.today() - timedelta(weeks=1)
        with override_settings(CHORE_ROTATION_START_DATE=start):
            for chore in self.chores:
                ChoreCompletion.objects.create(chore=chore, week_index=0, done=False)
            response = self.client.get(reverse("dashboard"))

        self.assertTrue(all(row["overdue"] for row in response.context["rows"]))

    def test_not_overdue_when_previous_week_marked_done(self):
        start = date.today() - timedelta(weeks=1)
        with override_settings(CHORE_ROTATION_START_DATE=start):
            for chore in self.chores:
                ChoreCompletion.objects.create(chore=chore, week_index=0, done=True)
            response = self.client.get(reverse("dashboard"))

        self.assertTrue(all(not row["overdue"] for row in response.context["rows"]))


class ToggleDoneViewTests(TestCase):
    def setUp(self):
        self.chore = Chore.objects.create(name="Dishes", order=1)

    def test_get_is_not_allowed(self):
        response = self.client.get(reverse("toggle-chore", args=[self.chore.id]))
        self.assertEqual(response.status_code, 405)

    def test_post_marks_done_then_toggling_again_undoes_it(self):
        start = date.today()
        with override_settings(CHORE_ROTATION_START_DATE=start):
            week = week_index(start, date.today())
            url = reverse("toggle-chore", args=[self.chore.id])

            response = self.client.post(url)
            self.assertRedirects(response, reverse("dashboard"))
            completion = ChoreCompletion.objects.get(chore=self.chore, week_index=week)
            self.assertTrue(completion.done)
            self.assertIsNotNone(completion.completed_at)

            self.client.post(url)
            completion.refresh_from_db()
            self.assertFalse(completion.done)
            self.assertIsNone(completion.completed_at)

    def test_post_with_unknown_chore_id_returns_404(self):
        response = self.client.post(reverse("toggle-chore", args=[999999]))
        self.assertEqual(response.status_code, 404)
