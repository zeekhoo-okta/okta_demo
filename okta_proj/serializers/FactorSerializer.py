from rest_framework import serializers
from LinksSerializer import LinksSerializer


class FactorSerializer(serializers.Serializer):
    id = serializers.CharField()
    factorType = serializers.CharField()
    provider = serializers.CharField()
    links = LinksSerializer(required=False)


