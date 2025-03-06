from django.contrib import admin
from .models import Account, Session, Score, Multiplayer

# Register your models here.

class AccountAdmin(admin.ModelAdmin):
    list_display = ("username", "password")

class SessionAdmin(admin.ModelAdmin):
    list_display = ("id", "player1", "player2", "is_multiplayer", "created_at", "ended_at")

class ScoreAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "player", "score", "won")

class MultiplayerAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "player1_ready", "player2_ready", "game_started")


admin.site.register(Account, AccountAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(Score, ScoreAdmin)
admin.site.register(Multiplayer, MultiplayerAdmin)