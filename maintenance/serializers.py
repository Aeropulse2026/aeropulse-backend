from rest_framework import serializers

from fleet.models import Aircraft, InventoryPart, Subsystem
from squadron.models import Squadron

from .models import AssetPart, MaintenanceTask


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


class SparePartDetailSerializer(serializers.ModelSerializer):
    compatible_subsystem = serializers.SlugRelatedField(read_only=True, slug_field="code")
    available_stock = serializers.ReadOnlyField()

    class Meta:
        model = InventoryPart
        fields = [
            "part_id",
            "name",
            "compatible_subsystem",
            "stock_on_hand",
            "reserved_stock",
            "available_stock",
            "reorder_point",
            "lead_days",
        ]


class SparePartSerializer(serializers.ModelSerializer):
    compatible_subsystem = serializers.SlugRelatedField(
        slug_field="code",
        queryset=Subsystem.objects.all(),
    )
    available_stock = serializers.ReadOnlyField()

    class Meta:
        model = InventoryPart
        fields = [
            "id",
            "part_id",
            "name",
            "compatible_subsystem",
            "stock_on_hand",
            "reserved_stock",
            "available_stock",
            "reorder_point",
            "lead_days",
            "updated_at",
        ]
        read_only_fields = ["id", "available_stock", "updated_at"]


class AssetPartSerializer(serializers.ModelSerializer):
    aircraft = serializers.SlugRelatedField(
        slug_field="aircraft_id",
        queryset=Aircraft.objects.all(),
    )
    spare_part = serializers.SlugRelatedField(
        source="inventory_part",
        slug_field="part_id",
        queryset=InventoryPart.objects.all(),
    )
    spare_part_details = SparePartDetailSerializer(source="inventory_part", read_only=True)

    class Meta:
        model = AssetPart
        fields = [
            "id",
            "aircraft",
            "spare_part",
            "spare_part_details",
            "serial_number",
            "installed_location",
            "installed_on",
            "last_maintained_on",
            "next_maintenance_on",
            "status",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "spare_part_details", "created_at", "updated_at"]
