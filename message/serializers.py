from rest_framework import serializers
from .models import Message, FileUpload

class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields = "__all__"

class MessageSerializer(serializers.ModelSerializer):
    file = serializers.PrimaryKeyRelatedField(
        queryset=FileUpload.objects.all(), required=False, allow_null=True
    )  # File attachment as an optional reference

    class Meta:
        model = Message
        fields = ["id", "sender", "receiver", "text", "file", "timestamp"]

    def create(self, validated_data):
        file_instance = validated_data.pop("file", None)
        message = Message.objects.create(**validated_data)

        if file_instance:
            message.file = file_instance
            message.save()

        return message

    def to_representation(self, instance):
        """Modify output to include file details if attached."""
        data = super().to_representation(instance)
        if instance.file:
            data["file"] = FileUploadSerializer(instance.file).data
        return data
