from datetime import date


def week_index(start_date: date, today: date) -> int:
    """Number of whole weeks elapsed between start_date and today.

    Week 0 covers [start_date, start_date + 7 days).
    """
    if today < start_date:
        raise ValueError("today cannot be before start_date")
    return (today - start_date).days // 7


def current_assignments(people, chores, start_date: date, today: date):
    """Return this week's chore -> person assignments.

    Each chore rotates through `people` on a weekly cadence, offset by its
    own position in `chores` so that, within a single week, different
    chores land on different people (a round-robin schedule) rather than
    everyone's turn changing in lockstep.

    `people` and `chores` may be any indexable sequence (e.g. plain values
    or Django model instances) ordered the way they should rotate/list.

    Returns a list of (chore, person) tuples, in the same order as `chores`.
    """
    if not people:
        raise ValueError("people must not be empty")

    week = week_index(start_date, today)
    num_people = len(people)

    return [
        (chore, people[(week + chore_index) % num_people])
        for chore_index, chore in enumerate(chores)
    ]
