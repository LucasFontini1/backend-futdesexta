"""Equipes privadas e convites: o acesso é controlado no servidor."""
from datetime import timedelta
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone


def invitation_expiry():
    return timezone.now() + timedelta(days=7)


class Team(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#22c55e')
    emblem = models.ImageField(upload_to='teams/', blank=True, null=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='owned_teams'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class TeamMembership(models.Model):
    class Role(models.TextChoices):
        OWNER = 'owner', 'Dono'
        ADMIN = 'admin', 'Administrador'
        MEMBER = 'member', 'Membro'

    team = models.ForeignKey(Team, related_name='memberships', on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='team_memberships', on_delete=models.CASCADE
    )
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['team', 'user'], name='unique_team_user'),
        ]


class TeamInvitation(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendente'
        ACCEPTED = 'accepted', 'Aceito'
        DECLINED = 'declined', 'Recusado'
        CANCELED = 'canceled', 'Cancelado'
        EXPIRED = 'expired', 'Expirado'

    team = models.ForeignKey(Team, related_name='invitations', on_delete=models.CASCADE)
    invitee = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='team_invitations', on_delete=models.CASCADE
    )
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='sent_team_invitations', on_delete=models.CASCADE
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=invitation_expiry)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['team', 'invitee'],
                condition=Q(status='pending'),
                name='unique_pending_team_invitation',
            ),
        ]


class Player(models.Model):
    team = models.ForeignKey(Team, related_name='players', on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    shirt_number = models.PositiveSmallIntegerField(blank=True, null=True)
    position = models.CharField(max_length=40, blank=True)
    photo = models.ImageField(upload_to='players/', blank=True, null=True)
    linked_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='player_profiles',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['team', 'shirt_number'],
                condition=Q(shirt_number__isnull=False),
                name='unique_player_shirt_per_team',
            ),
            models.UniqueConstraint(
                fields=['team', 'linked_user'],
                condition=Q(linked_user__isnull=False),
                name='unique_player_link_per_team',
            ),
        ]
