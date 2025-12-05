from django.urls import path
from .views import login_user, signin_user, logout_user, update_user, getAvatar, oauth_login_user, oauth_callback, user_keymap

app_name = "accounts"


urlpatterns = [
    path("login/", login_user, name="login"),
    path("signin/", signin_user, name="signin"),
    path("logout/", logout_user, name="logout"),
    path("update/", update_user, name="update_user"),
    path("avatar/", getAvatar, name="avatar"),
    path("oauth/login/", oauth_login_user, name="oauth_login"),
    path("oauth/callback/", oauth_callback, name="oauth_callback"),
    path("keymap/", user_keymap, name="user_keymap")
]
