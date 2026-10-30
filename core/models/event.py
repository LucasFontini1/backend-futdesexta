"""Eventos das equipes e presença Vou/Não vou."""
from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


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
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, validators=[MinValueValidator(-180), MaxValueValidator(180)])
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
