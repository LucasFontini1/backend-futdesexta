"""Escalação manual, resultados e eventos oficiais da partida."""
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class MatchSide(models.Model):
    match = models.ForeignKey('core.Match', on_delete=models.CASCADE, related_name='sides')
    team = models.ForeignKey(
        'core.Team', on_delete=models.PROTECT, related_name='match_sides', null=True, blank=True
    )
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#22c55e')
    order = models.PositiveSmallIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['match', 'order'], name='unique_match_side_order'),
            models.UniqueConstraint(fields=['match', 'name'], name='unique_match_side_name'),
        ]
        ordering = ['order']


class LineupSlot(models.Model):
    match = models.ForeignKey('core.Match', on_delete=models.CASCADE, related_name='lineup_slots')
    side = models.ForeignKey(MatchSide, on_delete=models.CASCADE, related_name='lineup_slots')
    player = models.ForeignKey('core.Player', on_delete=models.PROTECT, related_name='lineup_slots')
    position = models.CharField(max_length=40, blank=True)
    goalkeeper = models.BooleanField(default=False)
    reserve = models.BooleanField(default=False)
    x = models.PositiveSmallIntegerField(default=50, validators=[MaxValueValidator(100)])
    y = models.PositiveSmallIntegerField(default=50, validators=[MaxValueValidator(100)])

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['match', 'player'], name='unique_player_per_match'),
        ]


class MatchResult(models.Model):
    match = models.OneToOneField('core.Match', on_delete=models.CASCADE, related_name='result')
    home_side = models.ForeignKey(MatchSide, on_delete=models.PROTECT, related_name='+')
    away_side = models.ForeignKey(MatchSide, on_delete=models.PROTECT, related_name='+')
    home_score = models.PositiveSmallIntegerField()
    away_score = models.PositiveSmallIntegerField()
    entered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    updated_at = models.DateTimeField(auto_now=True)


class GoalEvent(models.Model):
    result = models.ForeignKey(MatchResult, on_delete=models.CASCADE, related_name='goals')
    scoring_side = models.ForeignKey(MatchSide, on_delete=models.PROTECT)
    scorer = models.ForeignKey(
        'core.Player', null=True, blank=True, on_delete=models.SET_NULL, related_name='goal_events'
    )
    conceded_by = models.ForeignKey(
        'core.Player', null=True, blank=True, on_delete=models.SET_NULL, related_name='goals_conceded'
    )
    own_goal = models.BooleanField(default=False)
    minute = models.PositiveSmallIntegerField(null=True, blank=True)


class ResultRevision(models.Model):
    result = models.ForeignKey(MatchResult, on_delete=models.CASCADE, related_name='revisions')
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    before = models.JSONField(default=dict)
    after = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)
