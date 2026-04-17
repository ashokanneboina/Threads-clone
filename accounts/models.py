
from ssl import ALERT_DESCRIPTION_INSUFFICIENT_SECURITY
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

from django.db.models.fields.related_lookups import RelatedExact
# Create your models here.

class CustomUser(AbstractUser):
    """
    User model
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    


class Profile(models.Model):
    """
    Profile model
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    
    bio = models.TextField(blank=True)
    
    profile_pic = models.BinaryField(null=True, blank=True)
    

class Follows(models.Model):
    """
    follows model
    """
    follow_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    follower_id = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    following_id = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='following'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('follower_id', 'following_id')
    
    


class Thread(models.Model):
   user = models.ForeignKey(
       CustomUser,
       on_delete=models.CASCADE,
       related_name="threads"
   )
   content = models.TextField()
   image = models.BinaryField(null=True, blank=True)
   created_at = models.DateTimeField(auto_now_add=True)
   
  

class Like(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )
    thread = models.ForeignKey(
        Thread,
        on_delete=models.CASCADE,
        related_name="likes"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'thread']
        

class Saved(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )
    thread = models.ForeignKey(
        Thread,
        on_delete=models.CASCADE,
        related_name="saved"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'thread']