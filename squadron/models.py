from django.conf import settings
from django.db import models

# Create your models here.

class Squadron(models.Model):
    squadron_id = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=120)
    base = models.CharField(max_length=80, blank=True)
    aircraft_count = models.PositiveSmallIntegerField(null=True, blank=True)
    aircraft_type = models.CharField(max_length=80, blank=True)
    operational_role = models.CharField(max_length=80, blank=True)
    source_url = models.URLField(blank=True)
    source_last_synced_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class SquadronAircraft(models.Model):
    """An individually identifiable aircraft assigned to an IAF squadron."""

    squadron = models.ForeignKey(
        Squadron,
        on_delete=models.CASCADE,
        related_name="fleet_aircraft",
    )
    aircraft_number = models.CharField(max_length=40, unique=True)
    aircraft_name = models.CharField(max_length=120)
    country_of_origin = models.CharField(max_length=80)
    year_inducted = models.PositiveSmallIntegerField()
    flight_hours = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    last_maintenance_on = models.DateField(null=True, blank=True)
    next_maintenance_on = models.DateField(null=True, blank=True)
    operational_role = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["squadron__squadron_id", "aircraft_number"]
        indexes = [
            models.Index(
                fields=["squadron", "next_maintenance_on"],
                name="sqd_ac_next_maint_idx",
            ),
        ]

    def __str__(self):
        return f"{self.aircraft_number} — {self.aircraft_name}"
