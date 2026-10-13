from rest_framework import viewsets

from .models import MaintenanceTask
from .serializers import MaintenanceTaskSerializer


class MaintenanceTaskViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceTask.objects.select_related("aircraft", "squadron").all()
    serializer_class = MaintenanceTaskSerializer
