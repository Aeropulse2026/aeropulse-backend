from rest_framework import viewsets

from .models import Squadron, SquadronAircraft
from .serializers import SquadronAircraftSerializer, SquadronSerializer


class SquadronViewSet(viewsets.ModelViewSet):
    queryset = Squadron.objects.all().order_by("squadron_id")
    serializer_class = SquadronSerializer
    lookup_field = "squadron_id"


class SquadronAircraftViewSet(viewsets.ModelViewSet):
    serializer_class = SquadronAircraftSerializer
    lookup_field = "aircraft_number"

    def get_queryset(self):
        queryset = SquadronAircraft.objects.select_related("squadron")
        squadron_id = self.request.query_params.get("squadron")
        if squadron_id:
            queryset = queryset.filter(squadron__squadron_id=squadron_id)
        return queryset.order_by("squadron__squadron_id", "aircraft_number")
