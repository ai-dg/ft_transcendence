from django.contrib.auth import get_user_model
from django.db import models
import uuid


class Ban(models.Model):
    banned_by = models.ForeignKey(get_user_model(), related_name='banned_by', on_delete=models.CASCADE)
    banned_user = models.ForeignKey(get_user_model(), related_name='banned_user', on_delete=models.CASCADE)
    reason = models.TextField(blank=True)
    ban_date = models.DateTimeField(auto_now_add=True)


class Room(models.Model):
    room_id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True, editable=False) 
    system_name = models.CharField(max_length=255, blank=True, null=True, unique=True) 
    custom_name = models.CharField(max_length=255, blank=True, null=True) 
    creator = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="created_rooms", blank=True, null=True)
    invited = models.ManyToManyField(get_user_model(), related_name="rooms", blank=True)  

    def __str__(self):
        return f"Room: {self.custom_name or 'Unnamed Room'} (Created by {self.creator.username if self.creator else 'Unknown'})"

class Messages(models.Model):
    message = models.TextField()
    read_at = models.DateTimeField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="messages")
    modified = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Message from {self.author} to {self.recipients.count()} recipient(s)"

