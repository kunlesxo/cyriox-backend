from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class FileUpload(models.Model):
    file = models.FileField(upload_to="uploads/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name

class Message(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages"
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_messages"
    )
    text = models.TextField(null=True, blank=True)
    file = models.ForeignKey(
        FileUpload, null=True, blank=True, on_delete=models.SET_NULL, related_name="messages"
    )  # Attach file
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver}"
