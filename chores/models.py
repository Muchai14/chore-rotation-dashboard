from django.db import models


class Person(models.Model):
    """A housemate in the rotation. Order determines turn sequence."""

    name = models.CharField(max_length=100, unique=True)
    order = models.PositiveIntegerField(unique=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name


class Chore(models.Model):
    """A chore in the fixed list. Order determines its position in the list."""

    name = models.CharField(max_length=100, unique=True)
    order = models.PositiveIntegerField(unique=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name


class ChoreCompletion(models.Model):
    """Whether a given chore was marked done for a given rotation week.

    `week_index` is the week number since the project's rotation start date
    (see chores.services.week_index) — not a calendar ISO week — so it stays
    consistent with the rotation logic used to compute assignments.
    """

    chore = models.ForeignKey(Chore, on_delete=models.CASCADE, related_name="completions")
    week_index = models.PositiveIntegerField()
    done = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["chore", "week_index"], name="unique_chore_week_completion"
            )
        ]
        ordering = ["week_index", "chore__order"]

    def __str__(self):
        status = "done" if self.done else "not done"
        return f"{self.chore} (week {self.week_index}): {status}"
