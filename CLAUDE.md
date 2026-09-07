# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Django app for a shared household chore rotation dashboard: a fixed list of
chores rotates through 4 housemates one at a time, advancing weekly. No
accounts — everyone uses the same link. See `chore-tool-scope.md` for the
full agreed scope and `_docs/plan.md` / `_docs/backlog.md` for design
rationale and the (now complete) task backlog.

## Commands

All commands assume the virtualenv is active:

```
source venv/bin/activate
```

- Run dev server: `python manage.py runserver`
- Run all tests: `python manage.py test chores`
- Run a single test: `python manage.py test chores.tests.ClassName.test_method_name`
- Make/apply migrations after model changes: `python manage.py makemigrations chores && python manage.py migrate`
- Populate the fixed people/chore lists: `python manage.py seed_chores` (safe to re-run; upserts by name)
- Check production settings without deploying: `python manage.py check --deploy`
- After adding a dependency: `pip install <package>` then `pip freeze > requirements.txt`

## Architecture

Single Django app (`chores`) inside the `chorehub` project. The core design
decision, from `_docs/plan.md`, is that **rotation assignments are computed,
not stored** — there is no table of "who's doing what this week." Instead:

- `chores/services.py` has two pure functions: `week_index(start_date, today)`
  (weeks elapsed since a reference date — **not** a calendar ISO week) and
  `current_assignments(people, chores, start_date, today)`, which offsets each
  chore by its own list position so different chores land on different people
  within the same week (a round-robin/Latin-square schedule). Both take plain
  ordered sequences, not querysets, so they're tested without the DB.
- `CHORE_ROTATION_START_DATE` in `chorehub/settings.py` is the one fixed
  reference point rotation counts weeks from; changing it reshuffles every
  assignment.
- The only things persisted are `Person`/`Chore` (fixed lists, ordered via an
  `order` field, populated by the `seed_chores` management command — not
  editable through the UI) and `ChoreCompletion` (`chore`, `week_index`,
  `done`, `completed_at`), unique per `(chore, week_index)`.
- `chores/views.py`'s `dashboard` view computes the current week's
  assignments on every load by joining the computed rotation against
  whatever `ChoreCompletion` rows exist for that `week_index`. Overdue
  flagging works the same way one week back: if `week_index - 1` has no
  completion row or `done=False`, the chore is flagged overdue (week 0 is
  exempt — there's no previous week to check).
- `toggle_done` (POST-only) does a `get_or_create` on `ChoreCompletion` for
  the chore's current week and flips `done`, redirecting back to the
  dashboard. The checkbox in `chores/templates/chores/dashboard.html`
  auto-submits its form `onchange`.

### Settings / environment split

`chorehub/settings.py` branches on environment variables to support both
local dev and Render deployment from the same codebase:

- `DATABASE_URL` present → Postgres via `dj_database_url`; absent → SQLite
  (`db.sqlite3`). Local dev has no `DATABASE_URL`, so it always uses SQLite.
- `DJANGO_DEBUG` (defaults to `"True"`) gates `DEBUG`, which in turn gates:
  whitenoise's manifest static storage (needs `collectstatic` to have run,
  so it's production-only), and `SECURE_SSL_REDIRECT`/`SESSION_COOKIE_SECURE`/
  `CSRF_COOKIE_SECURE` (production-only, since Render terminates TLS and
  proxies plain HTTP).
- `RENDER_EXTERNAL_HOSTNAME` (injected by Render) feeds `ALLOWED_HOSTS`.
- `render.yaml` is the Render Blueprint: one web service (gunicorn) + one
  free Postgres database, with `DATABASE_URL` wired from the database to the
  service automatically. Render's free Postgres plan expires after 30 days —
  fine for trying it out, not for indefinite real use.

## Testing conventions

`chores/tests.py` avoids mocking the clock. Pure-function tests
(`WeekIndexTests`, `CurrentAssignmentsTests`) use fixed literal dates. View
tests (`DashboardViewTests`, `OverdueFlaggingTests`, `ToggleDoneViewTests`)
use `override_settings(CHORE_ROTATION_START_DATE=...)` with a start date
computed relative to `date.today()` (e.g. `date.today() - timedelta(weeks=1)`)
so they stay deterministic regardless of what day they're actually run.
