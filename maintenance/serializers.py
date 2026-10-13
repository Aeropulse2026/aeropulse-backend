from rest_framework import serializers

from .models import MaintenanceTask
from squadron.models import Squadron


class MaintenanceTaskSerializer(serializers.ModelSerializer):
    squadron = serializers.PrimaryKeyRelatedField(queryset=Squadron.objects.all())

    class Meta:
        model = MaintenanceTask
        fields = [
            "id",
            "aircraft",
            "squadron",
            "component",
            "action",
            "priority_score",
            "status",
            "scheduled_for",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
