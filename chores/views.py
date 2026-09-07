from datetime import date

from django.conf import settings
from django.shortcuts import render

from .models import Chore, ChoreCompletion, Person
from .services import current_assignments, week_index


def dashboard(request):
    people = list(Person.objects.all())
    chores = list(Chore.objects.all())

    if not people or not chores:
        return render(request, "chores/dashboard.html", {"rows": None})

    today = date.today()
    start_date = settings.CHORE_ROTATION_START_DATE
    week = week_index(start_date, today)

    completions_by_chore_id = {
        completion.chore_id: completion
        for completion in ChoreCompletion.objects.filter(week_index=week, chore__in=chores)
    }

    rows = [
        {
            "chore": chore,
            "person": person,
            "done": completions_by_chore_id.get(chore.id, None) is not None
            and completions_by_chore_id[chore.id].done,
        }
        for chore, person in current_assignments(people, chores, start_date, today)
    ]

    return render(request, "chores/dashboard.html", {"week_index": week, "rows": rows})
