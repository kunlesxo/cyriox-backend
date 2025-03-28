import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from notification.routing import websocket_urlpatterns as notification_ws
from message.routing import websocket_urlpatterns as chat_ws

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cyriox.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(notification_ws + chat_ws)
    ),
})
