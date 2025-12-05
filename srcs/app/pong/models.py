from django.db import models
from django.contrib.auth import get_user_model


class Session(models.Model):
    id = models.AutoField(primary_key=True)
    player1 = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="session_player1")
    player2 = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True, related_name="session_player2")
    is_multiplayer = models.BooleanField(default=False)
    player1_score = models.IntegerField(default=0)
    player2_score = models.IntegerField(default=0)
    ended_at = models.DateTimeField(auto_now_add=True)
    winner_id = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True, related_name="session_winner")
    is_tournament = models.BooleanField(default=False)
    tournament = models.ForeignKey("Tournament", on_delete=models.CASCADE, null=True, blank=True)
    round_number = models.IntegerField(default=1) #see for default argument
    previous_round_session1_id = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="next_round_session1_id")
    previous_round_session2_id = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="next_round_session2_id")

    def __str__(self):
        return f"Session: {self.id}, {self.player1.username} vs {self.player2.username if self.player2 else 'IA'}"

class Tournament(models.Model):
    uuid_str = models.CharField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    nb_rounds = models.IntegerField(default=1)
    winner_id = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True, related_name="won_tournaments")

    def __str__(self):
        return f"Tournament: {self.id} - {self.created_at} | {'Winner: ' if self.ended_at else 'Not ended yet'} {self.winner_id if self.ended_at else ''}"


class Multiplayer(models.Model):
    id = models.AutoField(primary_key=True)
    session = models.OneToOneField(Session, on_delete=models.CASCADE)
    player1_ready = models.BooleanField(default=False)
    player2_ready = models.BooleanField(default=False)
    game_started = models.BooleanField(default=False)

    def __str__(self):
        return f"Multiplayer {self.session.id} - {self.session.player1.username} vs {self.session.player2.username if self.session.player2 else 'IA'}"  # ✅ Assure que .username est utilisé
