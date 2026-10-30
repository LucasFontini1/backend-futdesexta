"""Competições entre equipes registradas no Fut de Sexta."""
from django.conf import settings
from django.db import models


class Competition(models.Model):
    class Format(models.TextChoices):
        LEAGUE = 'league', 'Pontos corridos'
        KNOCKOUT = 'knockout', 'Mata-mata'

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='competitions_owned')
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='competitions/', null=True, blank=True)
    rules = models.TextField(blank=True)
    format = models.CharField(max_length=12, choices=Format.choices)
    starts_on = models.DateField(null=True, blank=True)
    ends_on = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class CompetitionAdmin(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='administrators')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['competition', 'user'], name='unique_competition_admin'),
        ]


class CompetitionInvitation(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendente'
        ACCEPTED = 'accepted', 'Aceito'
        DECLINED = 'declined', 'Recusado'

    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='invitations')
    team = models.ForeignKey('core.Team', on_delete=models.CASCADE, related_name='competition_invitations')
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['competition', 'team'], name='unique_competition_invitation'),
        ]


class CompetitionTeam(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='participants')
    team = models.ForeignKey('core.Team', on_delete=models.PROTECT, related_name='competition_participations')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['competition', 'team'], name='unique_competition_participant'),
        ]


class CompetitionFixture(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='fixtures')
    match = models.OneToOneField('core.Match', on_delete=models.CASCADE, related_name='competition_fixture')
    home_team = models.ForeignKey('core.Team', on_delete=models.PROTECT, related_name='home_fixtures')
    away_team = models.ForeignKey('core.Team', on_delete=models.PROTECT, related_name='away_fixtures')
    round = models.PositiveSmallIntegerField(default=1)
    winner = models.ForeignKey('core.Team', on_delete=models.PROTECT, null=True, blank=True, related_name='+')

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(home_team=models.F('away_team')),
                name='different_competition_fixture_teams',
            ),
        ]
