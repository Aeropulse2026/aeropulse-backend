from django.db import models

from fleet.models import Aircraft, InventoryPart
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


class AssetPart(models.Model):
    """A serialized spare part installed on a specific aircraft."""

    class Status(models.TextChoices):
        INSTALLED = "installed", "Installed"
        IN_SERVICE = "in_service", "In service"
        UNDER_MAINTENANCE = "under_maintenance", "Under maintenance"
        RETIRED = "retired", "Retired"

    aircraft = models.ForeignKey(
        Aircraft,
        on_delete=models.PROTECT,
        related_name="asset_parts",
    )
    inventory_part = models.ForeignKey(
        InventoryPart,
        on_delete=models.PROTECT,
        related_name="asset_assignments",
    )
    serial_number = models.CharField(max_length=80, unique=True)
    installed_location = models.CharField(max_length=100, blank=True)
    installed_on = models.DateField(null=True, blank=True)
    last_maintained_on = models.DateField(null=True, blank=True)
    next_maintenance_on = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=24,
        choices=Status.choices,
        default=Status.INSTALLED,
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["aircraft__aircraft_id", "serial_number"]
        indexes = [
            models.Index(
                fields=["aircraft", "status", "next_maintenance_on"],
                name="assetpart_aircraft_due_idx",
            ),
        ]

    def __str__(self):
        return f"{self.serial_number} — {self.inventory_part.name}"
