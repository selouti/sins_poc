from rest_framework import serializers
from .models import Customer, FieldDefinition


class FieldDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldDefinition
        fields = ["id", "key", "label", "active", "created_at"]
        read_only_fields = ["id", "created_at"]


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            "id",
            "surname",
            "name",
            "dob",
            "document_number",
            "extra_fields",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
