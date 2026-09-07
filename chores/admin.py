from django.contrib import admin

from .models import Chore, ChoreCompletion, Person


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ["order", "name"]
    ordering = ["order"]


@admin.register(Chore)
class ChoreAdmin(admin.ModelAdmin):
    list_display = ["order", "name"]
    ordering = ["order"]


@admin.register(ChoreCompletion)
class ChoreCompletionAdmin(admin.ModelAdmin):
    list_display = ["chore", "week_index", "done", "completed_at"]
    list_filter = ["week_index", "done"]
    ordering = ["-week_index", "chore__order"]
