from django.core.management.base import BaseCommand

from chores.models import Chore, Person

# Edit these two lists to match your actual housemates and chores. Order
# determines rotation order (people) and list position (chores).
PEOPLE = ["Alex", "Sam", "Jordan", "Taylor"]

CHORES = [
    "Dishes",
    "Trash & Recycling",
    "Bathroom Cleaning",
    "Vacuuming & Sweeping",
    "Kitchen Counters",
]


class Command(BaseCommand):
    help = "Seed the fixed Person and Chore lists (safe to re-run)."

    def handle(self, *args, **options):
        for index, name in enumerate(PEOPLE, start=1):
            person, created = Person.objects.update_or_create(
                name=name, defaults={"order": index}
            )
            self.stdout.write(
                f"{'Created' if created else 'Updated'} person: {person.name}"
            )

        for index, name in enumerate(CHORES, start=1):
            chore, created = Chore.objects.update_or_create(
                name=name, defaults={"order": index}
            )
            self.stdout.write(
                f"{'Created' if created else 'Updated'} chore: {chore.name}"
            )

        self.stdout.write(self.style.SUCCESS("Seeding complete."))
