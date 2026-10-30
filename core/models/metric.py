"""Estatísticas opcionais informadas pelos administradores de cada partida."""
from django.db import models


class MatchMetric(models.Model):
    """Um registro por jogador e partida; NULL significa não informado."""

    match = models.ForeignKey('core.Match', on_delete=models.CASCADE, related_name='metrics')
    player = models.ForeignKey('core.Player', on_delete=models.PROTECT, related_name='metrics')
    yellow_cards = models.PositiveSmallIntegerField(null=True, blank=True)
    red_cards = models.PositiveSmallIntegerField(null=True, blank=True)
    fouls = models.PositiveSmallIntegerField(null=True, blank=True)
    saves = models.PositiveSmallIntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['match', 'player'], name='unique_match_player_metric'),
        ]
