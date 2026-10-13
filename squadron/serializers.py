from rest_framework import serializers
from .models import Squadron, SquadronAircraft


class SquadronAircraftSerializer(serializers.ModelSerializer):
    squadron = serializers.SlugRelatedField(
        slug_field="squadron_id",
        queryset=Squadron.objects.all(),
    )

    class Meta:
        model = SquadronAircraft
        fields = [
            "id",
            "squadron",
            "aircraft_number",
            "aircraft_name",
            "country_of_origin",
            "year_inducted",
            "flight_hours",
            "last_maintenance_on",
            "next_maintenance_on",
            "operational_role",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

class SquadronSerializer(serializers.ModelSerializer):
    fleet_aircraft = SquadronAircraftSerializer(many=True, read_only=True)

    class Meta:
        model = Squadron
        fields = "__all__"
