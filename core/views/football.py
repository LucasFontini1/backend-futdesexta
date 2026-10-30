"""Operações oficiais de escalação e resultado; permissão verificada na API."""
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from core.models import GoalEvent, LineupSlot, Match, MatchResult, MatchSide, Player, ResultRevision
from core.serializers.football import (
    LineupSlotSerializer, MatchResultSerializer, MatchSideSerializer,
)
from core.views.team import is_admin


class MatchFootballActions:
    def assert_admin(self, match, user):
        authorized = is_admin(match.team, user)
        if match.kind == Match.Kind.FRIENDLY:
            authorized = authorized or match.sides.filter(
                team__memberships__user=user, team__memberships__role__in=['owner', 'admin']
            ).exists()
        if not authorized:
            raise PermissionDenied('Somente administradores registram resultados e escalações.')

    @action(detail=True, methods=['get', 'post'], url_path='lados')
    def sides(self, request, pk=None):
        match = self.get_object()
        if request.method == 'GET':
            return Response(MatchSideSerializer(match.sides.all(), many=True).data)
        self.assert_admin(match, request.user)
        if match.status == Match.Status.FINISHED:
            raise ValidationError('Não é possível modificar os lados de uma partida encerrada.')
        if match.sides.count() >= 2:
            raise ValidationError('Cada partida possui no máximo dois lados.')
        serializer = MatchSideSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        team = serializer.validated_data.get('team')
        if match.kind == Match.Kind.PELADA and team is not None:
            raise ValidationError('Peladas usam lados internos sem equipes adversárias.')
        if team and team != match.team and match.kind == Match.Kind.PELADA:
            raise ValidationError('Equipe inválida.')
        serializer.save(match=match)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get', 'put'], url_path='escalacao')
    def lineup(self, request, pk=None):
        match = self.get_object()
        if request.method == 'GET':
            return Response(LineupSlotSerializer(match.lineup_slots.all(), many=True).data)
        self.assert_admin(match, request.user)
        if match.status == Match.Status.FINISHED:
            raise ValidationError('Partida finalizada; não edite a escalação.')
        items = request.data.get('slots')
        if not isinstance(items, list):
            raise ValidationError({'slots': 'Informe a lista completa de escalação.'})
        serializer = LineupSlotSerializer(data=items, many=True)
        serializer.is_valid(raise_exception=True)
        existing = set()
        entries = []
        for item in serializer.validated_data:
            side, player = item['side'], item['player']
            if side.match_id != match.pk:
                raise ValidationError('Lado não pertence à partida.')
            allowed_team = side.team_id or match.team_id
            if player.team_id != allowed_team:
                raise ValidationError('Jogador não pertence à equipe deste lado.')
            if player.pk in existing:
                raise ValidationError('Jogador duplicado na escalação.')
            existing.add(player.pk)
            entries.append(LineupSlot(match=match, **item))
        with transaction.atomic():
            match.lineup_slots.all().delete()
            LineupSlot.objects.bulk_create(entries)
        return Response(LineupSlotSerializer(match.lineup_slots.all(), many=True).data)

    @action(detail=True, methods=['get', 'post'], url_path='resultado')
    def result(self, request, pk=None):
        match = self.get_object()
        result = MatchResult.objects.filter(match=match).first()
        if request.method == 'GET':
            if not result:
                return Response({'detail': 'Resultado ainda não registrado.'}, status=404)
            return Response(MatchResultSerializer(result).data)
        self.assert_admin(match, request.user)
        serializer = MatchResultSerializer(data=request.data, context={'match': match})
        serializer.is_valid(raise_exception=True)
        values = dict(serializer.validated_data)
        goals = values.pop('goals', None)
        with transaction.atomic():
            current = MatchResult.objects.select_for_update().filter(match=match).first()
            before = {}
            if current:
                before = {
                    'home_score': current.home_score,
                    'away_score': current.away_score,
                    'goals': list(current.goals.values('scoring_side_id', 'scorer_id', 'conceded_by_id')),
                }
                for key, value in values.items():
                    setattr(current, key, value)
                current.entered_by = request.user
                current.save()
            else:
                current = MatchResult.objects.create(match=match, entered_by=request.user, **values)
            if goals is not None:
                current.goals.all().delete()
                GoalEvent.objects.bulk_create([GoalEvent(result=current, **goal) for goal in goals])
            if match.kind == Match.Kind.FRIENDLY:
                from core.models import FriendlyInvitation
                FriendlyInvitation.objects.filter(match=match).update(
                    result_approved_from=False, result_approved_to=False
                )
                Match.objects.filter(pk=match.pk).update(status=Match.Status.IN_PROGRESS)
            else:
                Match.objects.filter(pk=match.pk).update(status=Match.Status.FINISHED)
            ResultRevision.objects.create(
                result=current, changed_by=request.user, before=before,
                after={'home_score': current.home_score, 'away_score': current.away_score},
            )
        return Response(MatchResultSerializer(current).data)
