from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Aircraft, ExternalFleetAircraft, InventoryPart, MaintenanceRecommendation, TelemetryImport, WorkOrder


class AircraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aircraft
        fields = "__all__"


class TelemetryImportSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelemetryImport
        fields = ["id", "file", "status", "created_at", "error_message"]
        read_only_fields = ["id", "status", "created_at", "error_message"]

    def validate_file(self, value):
        if not value.name.lower().endswith(".csv"):
            raise serializers.ValidationError("Only CSV telemetry files are accepted.")
        return value


class WorkOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkOrder
        fields = ["id", "aircraft", "component", "action", "priority_score", "status", "created_at", "required_part"]
        read_only_fields = ["id", "status", "created_at"]


class ExternalFleetAircraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalFleetAircraft
        fields = ["name", "category", "origin", "model_year", "active", "yoy_change", "ordered"]

class InventoryPartSerializer(serializers.ModelSerializer):
    available_stock = serializers.ReadOnlyField()
    class Meta:
        model = InventoryPart
        fields = ["part_id", "name", "stock_on_hand", "reserved_stock", "available_stock", "reorder_point", "lead_days", "updated_at"]

class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceRecommendation
        fields = ["id", "component", "required_part", "action", "reason", "due_by", "priority_score", "status", "created_at"]


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, style={"input_type": "password"})

    class Meta:
        model = get_user_model()
        fields = ["username", "email", "password"]
        extra_kwargs = {"email": {"required": False, "allow_blank": True}}

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)


class LoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.get_username()
        return token


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
