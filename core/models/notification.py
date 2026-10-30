"""Central de notificações e inscrições push isoladas por usuário."""
from django.conf import settings
from django.db import models


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications'
    )
    kind = models.CharField(max_length=60)
    title = models.CharField(max_length=255)
    link = models.CharField(max_length=255, blank=True)
    dedupe_key = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'dedupe_key'],
                condition=~models.Q(dedupe_key=''),
                name='unique_notification_dedupe_key',
            ),
        ]


class PushSubscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='push_subscriptions'
    )
    endpoint = models.URLField(max_length=1500, unique=True)
    p256dh = models.CharField(max_length=255)
    auth = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
