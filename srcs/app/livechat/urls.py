from django.urls import path
from . import views


app_name = "livechat"

urlpatterns = [
    path("online-users/", views.online_users, name="online-users"),
    path("create_channel/", views.create_channel, name="create_channel"),
    # path("delete/", views.delete_message, name="delete_message"),
    # path("update/", views.update_message, name="update_message"),
    # path("ban", views.ban_user, name="ban_user"),
    # path("unban", views.unban_user, name="unban_user"),
    # path("get_banned", views.get_banned, name="get_banned"),
    path("getmessages", views.get_messages, name="get_messages")
]