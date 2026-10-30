"""Representação de partidas e respostas de presença."""
from rest_framework import serializers
from core.models import Match, MatchAttendance


class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = [
            'id', 'team', 'title', 'kind', 'status', 'starts_at',
            'ends_at', 'location', 'latitude', 'longitude', 'expected_players', 'created_at',
        ]
        read_only_fields = ['id', 'kind', 'status', 'created_at']

    def validate(self, attrs):
        starts = attrs.get('starts_at', getattr(self.instance, 'starts_at', None))
        ends = attrs.get('ends_at', getattr(self.instance, 'ends_at', None))
        if starts and ends and ends <= starts:
            raise serializers.ValidationError({'ends_at': 'Término deve ser após o início.'})
        if self.instance and 'team' in attrs and attrs['team'].pk != self.instance.team_id:
            raise serializers.ValidationError({'team': 'Não é possível transferir a partida.'})
        return attrs


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchAttendance
        fields = ['user', 'response', 'updated_at']
        read_only_fields = ['user', 'updated_at']
