from django.urls import path, re_path
from . import views
from . import consumers

urlpatterns = [
    path("", views.pong, name="pong"),
    path("", views.pong, name="pong_index"),
    # path("start_game/", views.start_game),
    path("logout/", views.logout_view),
    path("getuser/", views.get_user),
    path("getusersessions/", views.get_user_sessions, name="get_user_session"),
    path("getuserstats/", views.get_user_stats, name="get_user_stats")
]
    # path("start_game/", views.start_game),