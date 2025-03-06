from django.urls import path
from . import views

urlpatterns = [
    path("", views.pong, name="pong"),
    path("start_game/", views.start_game),
    path("logout/", views.logout_view),
]