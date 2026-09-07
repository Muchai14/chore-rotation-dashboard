# Backlog

Small, ordered set of tasks for building the chore rotation dashboard in Django,
following the milestones in `plan.md`.

1. **Models** — Define `Person` and `Chore` in `chores/models.py` (fixed lists,
   ordered). Run `makemigrations`/`migrate`.

2. **Seed data** — Add a management command (`chores/management/commands/seed.py`)
   or a fixture to populate the fixed 4 people and chore list.

3. **Rotation logic** — Pure function in `chores/services.py`: given people,
   chores, a start date, and "today," return this week's assignments. Cover with
   unit tests in `chores/tests.py` across several weeks.

4. **Completion model** — Add `ChoreCompletion` model (`chore`, `iso_week`,
   `done`, `completed_at`) keyed by `(chore, iso_week)`. Migrate.

5. **Dashboard view** — `chores/views.py` + `chores/urls.py` (wired into
   `chorehub/urls.py`): render current week's assignments with a checkbox per
   chore.

6. **Mark-done endpoint** — View/form to toggle a `ChoreCompletion` for the
   current week; wire checkbox to POST and re-render.

7. **Overdue flagging** — On dashboard load, check last week's assignment
   completion; render a red "overdue" flag for anything left unchecked.

8. **Templates & styling** — Base template, dashboard template, minimal CSS for
   assignment list, checkboxes, and overdue flags.

9. **Admin registration** — Register `Chore`, `Person`, `ChoreCompletion` in
   `chores/admin.py` for easy debugging/inspection.

10. **Deploy target** — Decide hosting for the shared backend (open question
    from `plan.md`); add deployment config once chosen.
