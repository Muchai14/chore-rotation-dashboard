from datetime import date

from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

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


@require_POST
def toggle_done(request, chore_id):
    chore = get_object_or_404(Chore, id=chore_id)
    today = date.today()
    week = week_index(settings.CHORE_ROTATION_START_DATE, today)

    completion, _ = ChoreCompletion.objects.get_or_create(chore=chore, week_index=week)
    completion.done = not completion.done
    completion.completed_at = timezone.now() if completion.done else None
    completion.save()

    return redirect("dashboard")
