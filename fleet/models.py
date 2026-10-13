from django.conf import settings
from django.db import models

class Aircraft(models.Model):
    aircraft_id = models.CharField(max_length=32, unique=True)
    aircraft_type = models.CharField(max_length=80)
    age_years = models.PositiveSmallIntegerField()
    total_flight_hours = models.FloatField(default=0)
    total_cycles = models.PositiveIntegerField(default=0)
    base = models.CharField(max_length=80)
    health_score = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.aircraft_id


class UserProfile(models.Model):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        FLEET_MANAGER = "fleet_manager", "Fleet Manager"
        MAINTENANCE_ENGINEER = "maintenance_engineer", "Maintenance Engineer"
        STORE_OFFICER = "store_officer", "Store Officer"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=32, choices=Role.choices, default=Role.MAINTENANCE_ENGINEER)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class Subsystem(models.Model):
    code = models.SlugField(max_length=64, unique=True)
    name = models.CharField(max_length=100)
    service_interval_days = models.PositiveIntegerField(default=180)
    service_interval_cycles = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.name


class AircraftComponent(models.Model):
    aircraft = models.ForeignKey(Aircraft, on_delete=models.CASCADE, related_name="components")
    subsystem = models.ForeignKey(Subsystem, on_delete=models.PROTECT, related_name="components")
    serial_number = models.CharField(max_length=80, blank=True)
    installed_at = models.DateField(null=True, blank=True)
    last_serviced_at = models.DateField(null=True, blank=True)
    flight_hours_since_service = models.FloatField(default=0)
    cycles_since_service = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["aircraft", "subsystem"], name="one_component_per_aircraft_subsystem")]

    def __str__(self):
        return f"{self.aircraft_id} / {self.subsystem.code}"


class InventoryPart(models.Model):
    part_id = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=120)
    compatible_subsystem = models.ForeignKey(Subsystem, on_delete=models.PROTECT, related_name="parts")
    stock_on_hand = models.PositiveIntegerField(default=0)
    reserved_stock = models.PositiveIntegerField(default=0)
    reorder_point = models.PositiveIntegerField(default=0)
    lead_days = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def available_stock(self):
        return max(self.stock_on_hand - self.reserved_stock, 0)

    def __str__(self):
        return f"{self.part_id} - {self.name}"


class TelemetryImport(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETE = "complete", "Complete"
        FAILED = "failed", "Failed"

    file = models.FileField(upload_to="imports/%Y/%m/%d/")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    error_message = models.TextField(blank=True)


class TelemetryRecord(models.Model):
    component = models.ForeignKey(AircraftComponent, on_delete=models.CASCADE, related_name="telemetry")
    source_import = models.ForeignKey(TelemetryImport, on_delete=models.SET_NULL, null=True, blank=True, related_name="records")
    observed_at = models.DateTimeField()
    vibration_mm_s = models.FloatField(null=True, blank=True)
    temperature_c = models.FloatField(null=True, blank=True)
    pressure_psi = models.FloatField(null=True, blank=True)
    oil_level_pct = models.FloatField(null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["component", "observed_at"], name="one_reading_per_component_time")]
        indexes = [models.Index(fields=["component", "-observed_at"])]


class FaultEvent(models.Model):
    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    event_id = models.CharField(max_length=40, unique=True)
    component = models.ForeignKey(AircraftComponent, on_delete=models.CASCADE, related_name="fault_events")
    fault_code = models.CharField(max_length=80)
    severity = models.CharField(max_length=12, choices=Severity.choices)
    occurred_at = models.DateTimeField()
    resolved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        indexes = [models.Index(fields=["component", "-occurred_at"])]


class MaintenanceRecommendation(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        ACCEPTED = "accepted", "Accepted"
        DISMISSED = "dismissed", "Dismissed"

    component = models.ForeignKey(AircraftComponent, on_delete=models.CASCADE, related_name="recommendations")
    required_part = models.ForeignKey(InventoryPart, on_delete=models.SET_NULL, null=True, blank=True, related_name="recommendations")
    action = models.CharField(max_length=240)
    reason = models.TextField()
    due_by = models.DateTimeField(null=True, blank=True)
    priority_score = models.FloatField()
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)


class Prediction(models.Model):
    component = models.ForeignKey(AircraftComponent, on_delete=models.CASCADE, related_name="predictions")
    model_version = models.CharField(max_length=64)
    scored_at = models.DateTimeField(auto_now_add=True)
    anomaly_score = models.FloatField()
    failure_risk_score = models.FloatField()
    maintenance_due_score = models.FloatField()
    parts_risk_score = models.FloatField()
    health_score = models.FloatField()
    priority_score = models.FloatField()
    explanation_factors = models.JSONField(default=list)

    class Meta:
        indexes = [models.Index(fields=["component", "-scored_at"])]


class ExternalFleetSnapshot(models.Model):
    """A dated import from a public, third-party fleet-inventory page."""
    source_url = models.URLField()
    source_name = models.CharField(max_length=100, default="GlobalMilitary.net")
    source_updated_on = models.DateField(null=True, blank=True)
    retrieved_at = models.DateTimeField(auto_now_add=True)
    active_aircraft_total = models.PositiveIntegerField(null=True, blank=True)
    aircraft_on_order_total = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-retrieved_at"]


class ExternalFleetAircraft(models.Model):
    snapshot = models.ForeignKey(ExternalFleetSnapshot, on_delete=models.CASCADE, related_name="aircraft")
    category = models.CharField(max_length=40)
    name = models.CharField(max_length=120)
    origin = models.CharField(max_length=160, blank=True)
    model_year = models.PositiveSmallIntegerField(null=True, blank=True)
    active = models.PositiveIntegerField(null=True, blank=True)
    yoy_change = models.IntegerField(null=True, blank=True)
    ordered = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["snapshot", "name"], name="one_external_aircraft_per_snapshot")]
        ordering = ["category", "name"]


class WorkOrder(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending human approval"
        APPROVED = "approved", "Approved"
        ASSIGNED = "assigned", "Assigned"
        RESOLVED = "resolved", "Resolved"
        CANCELLED = "cancelled", "Cancelled"

    aircraft = models.ForeignKey(Aircraft, on_delete=models.CASCADE, related_name="work_orders")
    aircraft_component = models.ForeignKey(AircraftComponent, on_delete=models.PROTECT, related_name="work_orders", null=True, blank=True)
    recommendation = models.ForeignKey(MaintenanceRecommendation, on_delete=models.SET_NULL, related_name="work_orders", null=True, blank=True)
    required_part = models.ForeignKey(InventoryPart, on_delete=models.SET_NULL, related_name="work_orders", null=True, blank=True)
    component = models.CharField(max_length=100)
    action = models.CharField(max_length=240)
    priority_score = models.FloatField(default=0)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_work_orders")
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    downtime_hours = models.FloatField(null=True, blank=True)
    outcome = models.TextField(blank=True)
