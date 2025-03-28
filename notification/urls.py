from django.urls import path
from . import views  # Ensure `views.py` exists

urlpatterns = [
    path("notifications/", views.notification_view, name="notification_view"),  # Add a test route
]
