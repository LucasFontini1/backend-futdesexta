"""Convites administrativos para amistosos entre equipes cadastradas."""
from django.conf import settings
from django.db import models
from django.db.models import Q


class FriendlyInvitation(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendente'
        ACCEPTED = 'accepted', 'Aceito'
        DECLINED = 'declined', 'Recusado'
        CANCELED = 'canceled', 'Cancelado'

    from_team = models.ForeignKey('core.Team', related_name='sent_friendlies', on_delete=models.CASCADE)
    to_team = models.ForeignKey('core.Team', related_name='received_friendlies', on_delete=models.CASCADE)
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    match = models.OneToOneField(
        'core.Match', on_delete=models.SET_NULL, null=True, blank=True, related_name='friendly_invitation'
    )
    result_approved_from = models.BooleanField(default=False)
    result_approved_to = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=~Q(from_team=models.F('to_team')), name='friendlies_distinct_teams'
            ),
        ]
