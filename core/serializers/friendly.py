"""Amistosos privados; nomes básicos de equipe visíveis somente às envolvidas."""
from rest_framework import serializers
from core.models import FriendlyInvitation


class FriendlyInvitationSerializer(serializers.ModelSerializer):
    from_name = serializers.CharField(source='from_team.name', read_only=True)
    to_name = serializers.CharField(source='to_team.name', read_only=True)

    class Meta:
        model = FriendlyInvitation
        fields = [
            'id', 'from_team', 'from_name', 'to_team', 'to_name',
            'starts_at', 'ends_at', 'location', 'message', 'status',
            'match', 'result_approved_from', 'result_approved_to', 'created_at',
        ]
        read_only_fields = [
            'id', 'from_name', 'to_name', 'status', 'match',
            'result_approved_from', 'result_approved_to', 'created_at',
        ]

    def validate(self, data):
        if data['from_team'] == data['to_team']:
            raise serializers.ValidationError('Escolha equipes diferentes.')
        if data['ends_at'] <= data['starts_at']:
            raise serializers.ValidationError('O fim deve ser posterior ao início.')
        return data
