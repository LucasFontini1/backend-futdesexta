"""Regras de peladas semanais, com geração idempotente de ocorrências."""
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class RecurrenceRule(models.Model):
    team = models.ForeignKey('core.Team', on_delete=models.CASCADE, related_name='recurrences')
    title = models.CharField(max_length=120)
    weekday = models.PositiveSmallIntegerField(validators=[MaxValueValidator(6)])
    start_time = models.TimeField()
    end_time = models.TimeField()
    starts_on = models.DateField()
    until = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    expected_players = models.PositiveSmallIntegerField(default=10)
    interval_weeks = models.PositiveSmallIntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(8)]
    )
    active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)


class RecurrenceOccurrence(models.Model):
    rule = models.ForeignKey(RecurrenceRule, on_delete=models.CASCADE, related_name='occurrences')
    match = models.OneToOneField('core.Match', on_delete=models.CASCADE, related_name='recurrence_link')
    starts_at = models.DateTimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['rule', 'starts_at'], name='unique_recurrence_occurrence'),
        ]
