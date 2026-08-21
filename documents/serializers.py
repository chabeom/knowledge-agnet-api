from rest_framework import serializers

from documents.models import Document


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["id", "title", "content", "source", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
