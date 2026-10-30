"""Pedido de vinculação de um usuário a um jogador pré-cadastrado."""

from django.conf import settings
from django.db import models
from django.db.models import Q


class PlayerLinkRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendente'
        APPROVED = 'approved', 'Aprovado'
        REJECTED = 'rejected', 'Recusado'

    player = models.ForeignKey('core.Player', on_delete=models.CASCADE, related_name='link_requests')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='player_link_requests')
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['player', 'user'],
                condition=Q(status='pending'),
                name='unique_pending_player_link',
            ),
        ]
