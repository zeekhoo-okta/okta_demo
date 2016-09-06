from rest_framework import serializers
from FactorSerializer import FactorSerializer


class SessionSerializer(serializers.Serializer):
    id = serializers.CharField()
    userId = serializers.CharField()
    login = serializers.CharField()
    firstName = serializers.CharField()
    lastName = serializers.CharField()
    stateToken = serializers.CharField(required=False)
    factors = FactorSerializer(required=False, many=True)
