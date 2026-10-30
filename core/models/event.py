"""Eventos das equipes e presença Vou/Não vou."""
from django.conf import settings
from django.db import models


class TeamEvent(models.Model):
    team = models.ForeignKey('core.Team', related_name='events', on_delete=models.CASCADE)
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=40, default='other')
    image = models.ImageField(upload_to='events/', null=True, blank=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class EventAttendance(models.Model):
    class Response(models.TextChoices):
        GOING = 'going', 'Vou'
        NOT_GOING = 'not_going', 'Não vou'

    event = models.ForeignKey(TeamEvent, related_name='attendances', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    response = models.CharField(max_length=10, choices=Response.choices)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['event', 'user'], name='unique_event_attendance'),
        ]
