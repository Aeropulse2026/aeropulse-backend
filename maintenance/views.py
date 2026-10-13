from rest_framework import viewsets

from fleet.models import InventoryPart

from .models import AssetPart, MaintenanceTask
from .serializers import AssetPartSerializer, MaintenanceTaskSerializer, SparePartSerializer


class MaintenanceTaskViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceTask.objects.select_related("aircraft", "squadron").all()
    serializer_class = MaintenanceTaskSerializer


class AssetPartViewSet(viewsets.ModelViewSet):
    serializer_class = AssetPartSerializer
    lookup_field = "serial_number"

    def get_queryset(self):
        queryset = AssetPart.objects.select_related(
            "aircraft",
            "inventory_part",
            "inventory_part__compatible_subsystem",
        )
        aircraft_id = self.request.query_params.get("aircraft")
        if aircraft_id:
            queryset = queryset.filter(aircraft__aircraft_id=aircraft_id)
        return queryset.order_by("aircraft__aircraft_id", "serial_number")


class SparePartViewSet(viewsets.ModelViewSet):
    queryset = InventoryPart.objects.select_related("compatible_subsystem").all().order_by("part_id")
    serializer_class = SparePartSerializer
    lookup_field = "part_id"
