from django.urls import include, path
from rest_framework.routers import DefaultRouter

from fleet.views import (
    AircraftDetailView,
    AircraftRiskView,
    AircraftTelemetryView,
    FleetOverviewView,
    IafFleetView,
    InventoryForecastView,
    InventoryView,
    LoginView,
    LogoutView,
    MaintenanceQueueView,
    RecommendationView,
    RefreshView,
    SignUpView,
    TelemetryImportView,
    WorkOrderCreateView,
    WorkOrderDetailView,
)

from squadron.views import SquadronAircraftViewSet, SquadronViewSet
from maintenance.views import MaintenanceTaskViewSet

router = DefaultRouter()
router.register(
    "squadrons",
    SquadronViewSet,
    basename="squadron",
)
router.register(
    "squadron-aircraft",
    SquadronAircraftViewSet,
    basename="squadron-aircraft",
)

maintenance_router = DefaultRouter()
maintenance_router.register(
    "tasks",
    MaintenanceTaskViewSet,
    basename="maintenance-task",
)

auth_urlpatterns = [
    path("signup", SignUpView.as_view()),
    path("login", LoginView.as_view()),
    path("refresh", RefreshView.as_view()),
    path("logout", LogoutView.as_view()),
]

fleet_urlpatterns = [
    path("", include(router.urls)),
    path("imports/telemetry", TelemetryImportView.as_view(), name="telemetry-import"),
    path("overview", FleetOverviewView.as_view(), name="fleet-overview"),
    path("aircraft/<str:aircraft_id>", AircraftDetailView.as_view(), name="aircraft-detail"),
    path("aircraft/<str:aircraft_id>/telemetry", AircraftTelemetryView.as_view()),
    path("aircraft/<str:aircraft_id>/risk", AircraftRiskView.as_view()),
    path("maintenance/queue", MaintenanceQueueView.as_view(), name="maintenance-queue"),
    path("work-orders", WorkOrderCreateView.as_view(), name="work-order-create"),
    path("work-orders/<int:pk>", WorkOrderDetailView.as_view()),
    path("inventory", InventoryView.as_view()),
    path("inventory/forecast", InventoryForecastView.as_view()),
    path("recommendations", RecommendationView.as_view()),
    path("iaf/fleet", IafFleetView.as_view(), name="iaf-fleet"),
]

maintenance_urlpatterns = [
    path("", include(maintenance_router.urls)),
]

urlpatterns = [
    path("auth/", include(auth_urlpatterns)),
    path("fleet/", include(fleet_urlpatterns)),
    path("maintenance/", include(maintenance_urlpatterns)),
]
