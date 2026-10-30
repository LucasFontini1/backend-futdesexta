"""Serializadores de competições e convites."""
from rest_framework import serializers
from core.models import Competition, CompetitionFixture, CompetitionInvitation


class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = [
            'id', 'name', 'description', 'image', 'rules', 'format',
            'starts_on', 'ends_on', 'owner', 'is_active', 'created_at',
        ]
        read_only_fields = ['id', 'owner', 'created_at']

    def validate(self, data):
        start = data.get('starts_on', getattr(self.instance, 'starts_on', None))
        end = data.get('ends_on', getattr(self.instance, 'ends_on', None))
        if start and end and end < start:
            raise serializers.ValidationError('Data final deve vir após data inicial.')
        return data


class CompetitionInvitationSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source='team.name', read_only=True)
    class Meta:
        model = CompetitionInvitation
        fields = ['id', 'competition', 'team', 'team_name', 'status', 'sent_at']
        read_only_fields = fields


class CompetitionFixtureSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitionFixture
        fields = ['id', 'competition', 'match', 'home_team', 'away_team', 'round', 'winner']
        read_only_fields = fields
