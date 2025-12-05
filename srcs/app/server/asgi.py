# import os
# import django
# from django.core.asgi import get_asgi_application
# from channels.routing import ProtocolTypeRouter, URLRouter
# from django.urls import re_path, path
# from server.consumers import MyWebSocketConsumer

# """
# ASGI config for server project.

# It exposes the ASGI callable as a module-level variable named ``application``.

# For more information on this file, see
# https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
# """

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
# django.setup()

# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": URLRouter([
#         path("ws/", MyWebSocketConsumer.as_asgi()),
#     ]),
# })
import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")

django.setup()  # ✅ Charge Django avant les imports

from server.routing import websocket_urlpatterns  # ✅ Import après django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
