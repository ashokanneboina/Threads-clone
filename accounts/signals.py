from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser,Profile
from django.conf import settings
import os

@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance, created, **kwargs):
    if created:
        path = os.path.join(settings.BASE_DIR, 'media/defaults/default_profile_pic.jpg')
        with open(path, 'rb') as f:
            default_image = f.read()
        Profile.objects.create(
            user=instance,
            profile_pic=default_image
        )
        
        