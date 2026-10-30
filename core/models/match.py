"""Partidas e confirmação de presença. Uma modalidade por partida."""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.core.exceptions import ValidationError
from core.models.team import Team


class Match(models.Model):
    class Kind(models.TextChoices):
        PELADA = 'pelada', 'Pelada'
        FRIENDLY = 'friendly', 'Amistoso'
        COMPETITION = 'competition', 'Competição'

    class Status(models.TextChoices):
        SCHEDULED = 'scheduled', 'Agendada'
        CANCELED = 'canceled', 'Cancelada'
        IN_PROGRESS = 'in_progress', 'Em andamento'
        FINISHED = 'finished', 'Finalizada'

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches')
    title = models.CharField(max_length=120)
    kind = models.CharField(max_length=12, choices=Kind.choices, default=Kind.PELADA)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.SCHEDULED)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, validators=[MinValueValidator(-180), MaxValueValidator(180)])
    expected_players = models.PositiveSmallIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.ends_at and self.starts_at and self.ends_at <= self.starts_at:
            raise ValidationError({'ends_at': 'O término precisa ser posterior ao início.'})

    class Meta:
        ordering = ['starts_at']
        indexes = [models.Index(fields=['team', 'starts_at'])]


class MatchAttendance(models.Model):
    class Response(models.TextChoices):
        GOING = 'going', 'Vou'
        NOT_GOING = 'not_going', 'Não vou'

    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='attendances')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='match_attendances'
    )
    response = models.CharField(max_length=10, choices=Response.choices)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['match', 'user'], name='unique_match_attendance'),
        ]
