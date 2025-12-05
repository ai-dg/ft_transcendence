from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

class TranscendanceUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        # Do not create the user if username is not provided
        if not username:
            raise ValueError("The username field must be set")

        # Create the user
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        
        return user
    
    def create_superuser(self, username, password=None, **extra_fields):
        # Ensure the superuser has necessary permissions
        extra_fields.setdefault('is_staff', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        # Create user
        return self.create_user(username, password, **extra_fields)

def default_keys_map():
    return {
        "default_map": {
            'q' : ["move_up","stop"],
            'Q' : ["move_up","stop"],
            'd' : ["move_down","stop"],
            'D' : ["move_down","stop"],
            'ArrowLeft' : ["move_down","stop"],
            'ArrowRight' : ["move_up","stop"],
            'p' : ["pause_request", "noaction"],
            'space': ["launch", "noaction"]
        },
        "invited_map": {
            'q' : ["move_up","stop"],
            'Q' : ["move_up","stop"],
            'd' : ["move_down","stop"],
            'D' : ["move_down","stop"],
            'ArrowLeft' : ["move2_down", "stop2"],
            'ArrowRight' : ["move2_up", "stop2"],
            'p' : ["pause_request", "noaction"],
            'space': ["launch", "noaction"]
        },
        "invited_inverted_map": {
            'q' : ["move2_up", "stop2"],
            'Q' : ["move2_up", "stop2"],
            'd' : ["move2_down", "stop2"],
            'D' : ["move2_down", "stop2"],
            'ArrowLeft' : ["move_down","stop"],
            'ArrowRight' : ["move_up","stop"],
            'p' : ["pause_request", "noaction"],
            'space' : ["launch", "noaction"]
        },
    }

class TranscendanceUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=40, unique=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True) #to see how we do that
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    oauth = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    tournament_pseudo = models.CharField(max_length=40, blank=True)
    keys_map = models.JSONField(default=default_keys_map)
    
    friends = models.ManyToManyField('self', symmetrical=False, related_name="friend_of", blank=True)
    
    objects = TranscendanceUserManager()

    USERNAME_FIELD = "username" #field used as the UID for this user model
    REQUIRED_FIELDS = [] #required fields others than unique=True

    def __str__(self):
        return self.username