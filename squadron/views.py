from rest_framework import viewsets

from .models import Squadron
from .serializers import SquadronSerializer


class SquadronViewSet(viewsets.ModelViewSet):
    queryset = Squadron.objects.all().order_by("squadron_id")
    serializer_class = SquadronSerializer
    lookup_field = "squadron_id"
