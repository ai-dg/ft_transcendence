from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password, check_password

# Create your models here.
class Account(models.Model):
    username = models.CharField(unique=True, max_length=10)
    password = models.CharField(max_length=255)
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    # email = models.EmailField(unique=True)
    # password = models.CharField(max_length=255)

    # # groups = models.ManyToManyField(
    # #     "auth.Group",
    # #     related_name="account_users",
    # #     blank=True
    # # )

    # # user_permissions = models.ManyToManyField(
    # #     "auth.Permission",
    # #     related_name="account_permissions",
    # #     blank=True
    # # )

    def __str__(self):
        return f"Email: {self.username}"

class Session(models.Model):
    id = models.AutoField(primary_key=True)
    player1 = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="session_player1")
    player2 = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True, related_name="session_player2")
    is_multiplayer = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Session: {self.id}, {self.player1.username} vs {self.player2.username if self.player2 else 'IA'}"

class Score(models.Model):
    id = models.AutoField(primary_key=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    player = models.ForeignKey(Account, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    won = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.player.username}, score: {self.score}"

class Multiplayer(models.Model):
    id = models.AutoField(primary_key=True)
    session = models.OneToOneField(Session, on_delete=models.CASCADE)
    player1_ready = models.BooleanField(default=False)
    player2_ready = models.BooleanField(default=False)
    game_started = models.BooleanField(default=False)

    def __str__(self):
        return f"Multiplayer {self.session.id} - {self.session.player1.username} vs {self.session.player2.username if self.session.player2 else 'IA'}"  # ✅ Assure que .username est utilisé
