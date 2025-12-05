from django.urls import path, re_path
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

def get_websocket_urlpatterns():
    from pong.consumers import PongConsumer, PongGeneralConsumer, PongTournamentConsumer
    from livechat.consumers import ChatConsumer
    
    return [
        path("ws/game/", PongGeneralConsumer.as_asgi()),
        re_path(r'ws/chat/$', ChatConsumer.as_asgi()),
        re_path(r'^ws/pong/(?P<game_uid>[a-f0-9\-]+)/?$', PongConsumer.as_asgi()),
        re_path(r'^ws/pong/tournament/(?P<tournament_uid>[a-f0-9\-]+)/?$', PongTournamentConsumer.as_asgi()),
    ]

websocket_urlpatterns = get_websocket_urlpatterns()