from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
import uuid


# Create your models here.


class CustomUser(AbstractUser):
    """
    User model
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Profile(models.Model):
    """
    Profile model
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="profile"
    )

    bio = models.TextField(blank=True)

    profile_pic = models.BinaryField(null=True, blank=True)


class Follows(models.Model):
    """
    follows model
    """

    follow_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    follower_id = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="follower"
    )
    following_id = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="following"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower_id", "following_id")


class Thread(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="threads"
    )
    content = models.TextField()
    image = models.BinaryField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Like(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "thread"]


class Saved(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="saved")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "thread"]
        


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('follow', 'Follow'),
        ('like', 'Like'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="sent_notifications")
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="received_notifications")
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES)
    thread = models.ForeignKey(
        'Thread',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
   
    class Meta:
        indexes = [
            models.Index(fields=['receiver', '-created_at']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['sender', 'receiver', 'notification_type'],
                condition=Q(notification_type='follow', thread__isnull=True),
                name='unique_follow_notification',
            ),
            models.UniqueConstraint(
                fields=['sender', 'receiver', 'thread', 'notification_type'],
                condition=Q(notification_type='like'),
                name='unique_like_notification',
            )
        ]
        


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    thread = models.ForeignKey('Thread', on_delete=models.CASCADE, related_name="comments")


    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )

    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['thread', 'created_at']),
        ]


class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participants = models.ManyToManyField(
        CustomUser, related_name="conversations"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="sent_messages"
    )
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["conversation", "created_at"]),
        ]

   
