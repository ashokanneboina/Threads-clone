
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
    
    
    
