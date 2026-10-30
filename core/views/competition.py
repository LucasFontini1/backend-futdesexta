"""Administração independente de competições e acesso por equipe."""
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.models import (
    Competition, CompetitionAdmin, CompetitionFixture, CompetitionInvitation,
    CompetitionTeam, Match, MatchResult, MatchSide, Team,
)
from core.serializers.competition import (
    CompetitionFixtureSerializer, CompetitionInvitationSerializer, CompetitionSerializer,
)
from core.views.team import is_admin


def is_comp_admin(comp, user):
    return comp.owner_id == user.pk or CompetitionAdmin.objects.filter(
        competition=comp, user=user
    ).exists()


class CompetitionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CompetitionSerializer

    def get_queryset(self):
        return Competition.objects.filter(
            Q(owner=self.request.user) |
            Q(administrators__user=self.request.user) |
            Q(participants__team__memberships__user=self.request.user)
        ).distinct().order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        if not is_comp_admin(serializer.instance, self.request.user):
            raise PermissionDenied('Apenas organizadores podem editar.')
        serializer.save()

    def perform_destroy(self, instance):
        if not is_comp_admin(instance, self.request.user):
            raise PermissionDenied('Apenas organizadores podem encerrar.')
        instance.is_active = False
        instance.save(update_fields=['is_active'])

    @action(detail=True, methods=['post'], url_path='convidar')
    def invite(self, request, pk=None):
        comp = self.get_object()
        if not is_comp_admin(comp, request.user):
            raise PermissionDenied('Somente organizadores podem convidar.')
        team = get_object_or_404(Team, pk=request.data.get('team'))
        if CompetitionTeam.objects.filter(competition=comp, team=team).exists():
            raise ValidationError('Equipe já participa.')
        invite, created = CompetitionInvitation.objects.get_or_create(
            competition=comp, team=team
        )
        if not created and invite.status == CompetitionInvitation.Status.PENDING:
            raise ValidationError('Convite já enviado.')
        if not created:
            invite.status = CompetitionInvitation.Status.PENDING
            invite.save(update_fields=['status'])
        return Response(CompetitionInvitationSerializer(invite).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='equipes')
    def teams(self, request, pk=None):
        comp = self.get_object()
        return Response(list(comp.participants.values('team_id', 'team__name')))

    @action(detail=True, methods=['get', 'post'], url_path='jogos')
    def fixtures(self, request, pk=None):
        comp = self.get_object()
        if request.method == 'GET':
            return Response(CompetitionFixtureSerializer(comp.fixtures.all(), many=True).data)
        if not is_comp_admin(comp, request.user):
            raise PermissionDenied('Somente organizadores criam confrontos.')
        home = get_object_or_404(Team, pk=request.data.get('home_team'))
        away = get_object_or_404(Team, pk=request.data.get('away_team'))
        if home.pk == away.pk or not CompetitionTeam.objects.filter(competition=comp, team=home).exists() or not CompetitionTeam.objects.filter(competition=comp, team=away).exists():
            raise ValidationError('As duas equipes precisam participar da competição.')
        try:
            start = serializers.DateTimeField().run_validation(request.data.get('starts_at'))
            end = serializers.DateTimeField().run_validation(request.data.get('ends_at'))
        except Exception as exc:
            raise ValidationError('Informe início e fim válidos.') from exc
        if start >= end:
            raise ValidationError('O fim precisa ser após o início.')
        with transaction.atomic():
            match = Match.objects.create(
                team=home, kind=Match.Kind.COMPETITION, title=comp.name,
                starts_at=start, ends_at=end, location=request.data.get('location', ''),
            )
            MatchSide.objects.create(match=match, team=home, order=1, name=home.name)
            MatchSide.objects.create(match=match, team=away, order=2, name=away.name)
            fixture = CompetitionFixture.objects.create(
                competition=comp, match=match, home_team=home,
                away_team=away, round=int(request.data.get('round', 1)),
            )
        return Response(CompetitionFixtureSerializer(fixture).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='classificacao')
    def standings(self, request, pk=None):
        comp = self.get_object()
        rows = {
            item.team_id: {
                'team': item.team_id, 'name': item.team.name, 'points': 0,
                'played': 0, 'wins': 0, 'draws': 0, 'losses': 0,
                'goals_for': 0, 'goals_against': 0, 'goal_difference': 0,
            }
            for item in comp.participants.select_related('team')
        }
        for fixture in comp.fixtures.select_related('match'):
            result = MatchResult.objects.filter(
                match=fixture.match, match__status=Match.Status.FINISHED
            ).first()
            if not result:
                continue
            for team_id, scored, conceded in [
                (fixture.home_team_id, result.home_score, result.away_score),
                (fixture.away_team_id, result.away_score, result.home_score),
            ]:
                row = rows[team_id]
                row['played'] += 1
                row['goals_for'] += scored
                row['goals_against'] += conceded
                row['goal_difference'] += scored - conceded
                if scored > conceded:
                    row['wins'] += 1
                    row['points'] += 3
                elif scored == conceded:
                    row['draws'] += 1
                    row['points'] += 1
                else:
                    row['losses'] += 1
        return Response(sorted(rows.values(), key=lambda r: (-r['points'], -r['wins'], -r['goal_difference'], -r['goals_for'], r['name'])))


class CompetitionInvitationViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CompetitionInvitationSerializer

    def get_queryset(self):
        return CompetitionInvitation.objects.filter(
            Q(competition__owner=self.request.user) |
            Q(competition__administrators__user=self.request.user) |
            Q(team__memberships__user=self.request.user)
        ).distinct().order_by('-sent_at')

    @action(detail=True, methods=['post'], url_path='responder')
    def respond(self, request, pk=None):
        invite = self.get_object()
        if not is_admin(invite.team, request.user):
            raise PermissionDenied('Apenas donos e administradores da equipe respondem.')
        choice = request.data.get('accept')
        if not isinstance(choice, bool):
            raise ValidationError({'accept': 'Use true ou false.'})
        with transaction.atomic():
            invite = CompetitionInvitation.objects.select_for_update().get(pk=invite.pk)
            if invite.status != CompetitionInvitation.Status.PENDING:
                raise ValidationError('Convite já respondido.')
            invite.status = (
                CompetitionInvitation.Status.ACCEPTED if choice
                else CompetitionInvitation.Status.DECLINED
            )
            invite.save(update_fields=['status'])
            if choice:
                CompetitionTeam.objects.get_or_create(
                    competition=invite.competition, team=invite.team
                )
        return Response(self.get_serializer(invite).data)
