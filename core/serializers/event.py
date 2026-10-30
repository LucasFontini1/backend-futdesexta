"""Eventos e presenças controlados pela equipe."""
from rest_framework import serializers
from core.models import TeamEvent, EventAttendance


class TeamEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamEvent
        fields = [
            'id', 'team', 'title', 'description', 'category', 'image',
            'starts_at', 'ends_at', 'location', 'latitude', 'longitude', 'organizer', 'created_at',
        ]
        read_only_fields = ['id', 'organizer', 'created_at']

    def validate(self, data):
        if data.get('ends_at', getattr(self.instance, 'ends_at', None)) <= data.get(
            'starts_at', getattr(self.instance, 'starts_at', None)
        ):
            raise serializers.ValidationError('O término deve ser após o início.')
        return data


class EventAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventAttendance
        fields = ['user', 'response']
        read_only_fields = ['user']
