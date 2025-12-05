from django.contrib import admin
from .models import Session, Multiplayer, Tournament
from livechat.models import Ban

# Register your models here.

# class AccountAdmin(admin.ModelAdmin):
#     list_display = ("username", "password")

class SessionAdmin(admin.ModelAdmin):
    list_display = ("id", "player1", "player2", "is_multiplayer", "ended_at", "player1_score", "player2_score", "winner_id", "is_tournament", "tournament")

class TournamentAdmin(admin.ModelAdmin):
    list_display = ("uuid_str", "created_at", "ended_at", "winner_id")

class ScoreAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "player", "score", "won")

class MultiplayerAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "player1_ready", "player2_ready", "game_started")

class BanAdmin(admin.ModelAdmin):
    list_display = ("banned_by", "banned_user", "reason", "ban_date")


# admin.site.register(Account, AccountAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(Multiplayer, MultiplayerAdmin)
admin.site.register(Ban, BanAdmin)
admin.site.register(Tournament, TournamentAdmin)