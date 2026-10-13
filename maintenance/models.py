from django.db import models

from fleet.models import Aircraft
from squadron.models import Squadron


class MaintenanceTask(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    aircraft = models.ForeignKey(
        Aircraft,
        on_delete=models.CASCADE,
        related_name="maintenance_tasks",
    )
    squadron = models.ForeignKey(
        Squadron,
        on_delete=models.PROTECT,
        related_name="maintenance_tasks",
        null=True,
    )
    component = models.CharField(max_length=100)
    action = models.CharField(max_length=240)
    priority_score = models.FloatField(default=0)
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.PENDING,
    )
    scheduled_for = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-priority_score", "created_at"]

    def __str__(self):
        return f"{self.aircraft.aircraft_id} - {self.component}"
