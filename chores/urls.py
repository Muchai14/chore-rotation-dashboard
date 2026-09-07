from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("chores/<int:chore_id>/toggle/", views.toggle_done, name="toggle-chore"),
]
