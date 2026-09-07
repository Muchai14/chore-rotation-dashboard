# Implementation Plan

## Scope recap

See `chore-tool-scope.md` for the full agreed scope. Summary: 4 housemates, no auth,
fixed chore list (edited in code/config), chores rotate one person at a time on a
weekly cadence, "mark done" checkbox per week, unchecked items flagged overdue when
the week rolls over.

## Key design decision: rotation is computed, not stored

Since rotation always advances by a fixed weekly cadence in a fixed order, the
current assignment for any chore doesn't need to be stored — it can be computed
from:

- the chore's position in the fixed list
- the fixed list of 4 housemates
- the current ISO week number relative to a project start date

Only two things need to be persisted and shared across everyone's browser:

1. Which (chore, week) pairs have been marked done
2. The project start date (so week-over-week rotation stays consistent)

This keeps the data model small and avoids needing to store assignment history.

## Architecture

- **Frontend**: single-page web app. Fetches current week's chore/person
  assignments (computed client- or server-side) and renders checkboxes.
- **Backend**: minimal API (e.g. Node/Express) with a small persistent store
  (SQLite or a JSON file) for completion status, keyed by `(chore_id, iso_week)`.
- **Shared link**: no auth — the page loads the same shared state for anyone
  who opens it; users self-select their name from a dropdown/list, used only to
  filter "my chore this week," not for access control.

## Milestones

1. **Project scaffold** — repo, tooling, chore/person config file.
2. **Rotation logic** — pure function: given chore list, person list, start date,
   and current date → this week's assignments. Unit tested against several weeks.
3. **Completion tracking** — API + store for marking a chore done for the current
   week; frontend checkbox wired up.
4. **Overdue flagging** — on load, compare previous week's assignment completion
   status; render red flag for anything left unchecked.
5. **Polish & deploy** — basic styling, deploy target TBD.

## Open questions for later

- Hosting/deploy target for the shared backend.
- Exact overdue-flag lifecycle (does it clear after one week, or persist as a
  visible history of misses per person?).
