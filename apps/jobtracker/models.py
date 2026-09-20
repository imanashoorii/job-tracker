from django.conf import settings
from django.db import models

from apps.base.models import BaseModel, SoftDelete
from apps.jobtracker.choices import RoundChoices, StatusChoices


class Board(BaseModel, SoftDelete):
    """A tab in the tracker, e.g. 'Job Tracker 1'. Scoped to one user."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="boards",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "jobtracker_board"
        ordering = ["order", "id"]

    def __str__(self):
        return self.name


class Application(BaseModel, SoftDelete):
    board = models.ForeignKey(
        Board,
        related_name="applications",
        on_delete=models.CASCADE,
    )
    company = models.CharField(max_length=200, blank=True, default="")
    position = models.CharField(max_length=200, blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.APPLIED,
    )
    salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    round = models.CharField(
        max_length=10,
        choices=RoundChoices.choices,
        default=RoundChoices.NA,
    )
    notes = models.TextField(blank=True, default="")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "jobtracker_application"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.company} — {self.position}"
