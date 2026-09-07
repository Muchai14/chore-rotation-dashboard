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
