"""Controle de folgas em chaves mata-mata com número ímpar de equipes."""
from django.db import models


class CompetitionBye(models.Model):
    competition = models.ForeignKey('core.Competition', on_delete=models.CASCADE, related_name='byes')
    team = models.ForeignKey('core.Team', on_delete=models.CASCADE)
    round = models.PositiveSmallIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['competition', 'round', 'team'], name='unique_knockout_bye'),
        ]
