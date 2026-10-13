from django.contrib import admin
from .models import (Aircraft, AircraftComponent, ExternalFleetAircraft, ExternalFleetSnapshot, FaultEvent,
                     InventoryPart, MaintenanceRecommendation, Prediction, Subsystem, TelemetryImport,
                     TelemetryRecord, UserProfile, WorkOrder)
admin.site.register([Aircraft, Subsystem, AircraftComponent, InventoryPart, TelemetryImport, TelemetryRecord,
                     FaultEvent, MaintenanceRecommendation, Prediction, ExternalFleetSnapshot,
                     ExternalFleetAircraft, UserProfile, WorkOrder])
