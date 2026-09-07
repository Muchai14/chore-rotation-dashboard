# Chore Rotation Dashboard

A shared web dashboard for managing household chores among housemates. No accounts —
everyone uses the same link and picks their name.

## How it works

- A fixed list of chores rotates through 4 housemates, one person at a time.
- Rotation advances automatically every week.
- Each housemate can check off their chore as done for the current week.
- Anything left unchecked when the week turns over is flagged overdue (red).

## Local development

```
source venv/bin/activate
python manage.py migrate
python manage.py seed_chores   # populates the fixed people/chore lists
python manage.py runserver
```

Run tests with `python manage.py test chores`.

## Deployment (Render)

`render.yaml` defines the Render Blueprint for this app — a web service plus a
managed Postgres database. To deploy:

1. Push this repo to GitHub (already done for the `main` branch).
2. In the Render dashboard, choose **New > Blueprint** and point it at this repo.
   Render reads `render.yaml` and creates both the web service and the database.
3. `DJANGO_SECRET_KEY` is auto-generated; `DJANGO_DEBUG` is set to `False`; the
   database's `DATABASE_URL` is wired into the web service automatically.

Locally, the app still uses SQLite (`db.sqlite3`) by default — no `DATABASE_URL`
is set, so `DATABASES` falls back to it. This keeps local dev simple (no Postgres
install required) while production runs against real Postgres.

**Free-tier caveat:** Render's free Postgres plan expires (and is deleted) after
30 days. Fine for demos/trials — upgrade to a paid Postgres plan before relying on
this for real, ongoing household use.

## Status

Core features implemented: rotation logic, completion tracking, overdue flagging,
admin, tests, and a deploy config. See [`_docs/plan.md`](_docs/plan.md) and
[`_docs/backlog.md`](_docs/backlog.md) for the implementation plan, and
[`chore-tool-scope.md`](chore-tool-scope.md) for the agreed scope.
