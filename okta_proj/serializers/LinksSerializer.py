from rest_framework import serializers
from VerifySerializer import VerifySerializer


class LinksSerializer(serializers.Serializer):
    verify = VerifySerializer(required=False)
