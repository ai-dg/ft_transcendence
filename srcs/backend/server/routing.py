from django.urls import path
from django.core.asgi import get_asgi_application
from pong.consumers import PongConsumer, MyWebSocketConsumer
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

websocket_urlpatterns = [
    path("ws/", MyWebSocketConsumer.as_asgi()),
    path("ws/game/", PongConsumer.as_asgi()),
]

# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),  
#     "websocket": AuthMiddlewareStack(
#         URLRouter(websocket_urlpatterns)
#     ),
# })
