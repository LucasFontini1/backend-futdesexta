"""Validação de recorrências; não apagar partidas já realizadas."""

from rest_framework import serializers

from core.models import RecurrenceRule


class RecurrenceRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecurrenceRule
        fields = [
            'id',
            'team',
            'title',
            'weekday',
            'start_time',
            'end_time',
            'starts_on',
            'until',
            'location',
            'expected_players',
            'interval_weeks',
            'active',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate(self, data):
        start = data.get('start_time', getattr(self.instance, 'start_time', None))
        end = data.get('end_time', getattr(self.instance, 'end_time', None))
        starts_on = data.get('starts_on', getattr(self.instance, 'starts_on', None))
        until = data.get('until', getattr(self.instance, 'until', None))
        if start and end and end <= start:
            raise serializers.ValidationError({'end_time': 'Deve ser após o início.'})
        if starts_on and until and until < starts_on:
            raise serializers.ValidationError({'until': 'Data final inválida.'})
        return data
