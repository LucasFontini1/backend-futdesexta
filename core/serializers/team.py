"""Serialização com níveis separados para descoberta e membros."""

import re

from rest_framework import serializers

from core.models import Player, Team, TeamInvitation, TeamMembership


class TeamDiscoverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'name', 'emblem']
        read_only_fields = fields


class TeamSerializer(serializers.ModelSerializer):
    member_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Team
        fields = [
            'id',
            'name',
            'description',
            'color',
            'emblem',
            'owner',
            'created_at',
            'member_count',
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'member_count']

    def validate_color(self, value):
        if not re.fullmatch(r'#[0-9a-fA-F]{6}', value):
            raise serializers.ValidationError('Cor deve estar em formato #RRGGBB.')
        return value

    def validate_emblem(self, value):
        if value and value.size > 3 * 1024 * 1024:
            raise serializers.ValidationError('Imagem limitada a 3 MB.')
        return value


class TeamMembershipSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = TeamMembership
        fields = ['id', 'user', 'username', 'name', 'role', 'joined_at']
        read_only_fields = fields


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'name', 'shirt_number', 'position', 'photo', 'linked_user']
        read_only_fields = ['id', 'linked_user']

    def validate_photo(self, value):
        if value and value.size > 3 * 1024 * 1024:
            raise serializers.ValidationError('Imagem limitada a 3 MB.')
        return value

    def validate(self, attrs):
        team = self.context.get('team')
        number = attrs.get('shirt_number', getattr(self.instance, 'shirt_number', None))
        if team and number is not None:
            qs = Player.objects.filter(team=team, shirt_number=number)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({'shirt_number': 'Número já utilizado na equipe.'})
        return attrs


class TeamInvitationSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source='team.name', read_only=True)

    class Meta:
        model = TeamInvitation
        fields = [
            'id',
            'team',
            'team_name',
            'invitee',
            'invited_by',
            'status',
            'created_at',
            'expires_at',
        ]
        read_only_fields = fields
