# Household Chore Rotation Dashboard — Scope

## Users
- 4 housemates
- No accounts/auth — single shared link, users pick their name from a list

## Form Factor
- Shared web app / dashboard (browser-based)

## Chore List
- Flat list of chores (no recurrence/schedule config)
- List is fixed by the developer in code/config — not editable via the UI in v1

## Assignment Model
- Chores are picked from a shared pool (not pre-assigned to specific people)
- Rotation: each chore rotates through the 4 people one at a time
- Rotation trigger: fixed weekly cadence — advances to the next person every week, regardless of completion status

## Completion Tracking
- Checkbox to mark a chore "done" for the current week
- If not marked done by the time the week turns over:
  - Flagged visibly as overdue (e.g., red)
  - Rotation still advances to the next person as scheduled (no blocking)

## Out of Scope (v1)
- User accounts / authentication
- Editing the chore list from the UI
- Point systems, effort weighting, or claim-based assignment
- Recurring/scheduled chore definitions (e.g., daily vs. weekly per-chore)
