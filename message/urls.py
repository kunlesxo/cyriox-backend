from django.urls import path
from .views import MessageListCreateView, FileUploadView,  FileDeleteView

urlpatterns = [
    # Messaging Endpoints
    path("messages/", MessageListCreateView.as_view(), name="message-list-create"),
    
    # File Management Endpoints
    path("files/upload/", FileUploadView.as_view(), name="file-upload"),  # Upload file
    path("files/<int:file_id>/", FileDeleteView.as_view(), name="file-delete"),  # Delete file
]
