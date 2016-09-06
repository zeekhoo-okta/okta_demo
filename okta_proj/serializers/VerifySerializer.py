from rest_framework import serializers


class VerifySerializer(serializers.Serializer):
    href = serializers.CharField(allow_blank=True)
