from rest_framework import serializers
from .models import Squadron

class SquadronSerializer(serializers.ModelSerializer):
    class Meta:
        model = Squadron
        fields = '__all__'