"""Controle de acesso por objeto para equipes, jogadores e convites."""

from django.db import IntegrityError, transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import Player, Team, TeamInvitation, TeamMembership, User
from core.serializers import (
    PlayerSerializer,
    TeamDiscoverySerializer,
    TeamInvitationSerializer,
    TeamMembershipSerializer,
    TeamSerializer,
)
from core.services.notifications import notify_user
from core.views.team_management import TeamManagementActions


def is_admin(team, user):
    return TeamMembership.objects.filter(team=team, user=user, role__in=['owner', 'admin']).exists()


class TeamViewSet(TeamManagementActions, viewsets.ModelViewSet):
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_queryset(self):
        # Não retornar dados privados de equipes de terceiros.
        return (
            Team.objects
            .filter(memberships__user=self.request.user)
            .annotate(member_count=Count('memberships', distinct=True))
            .distinct()
            .order_by('id')
        )

    def perform_create(self, serializer):
        with transaction.atomic():
            team = serializer.save(owner=self.request.user)
            TeamMembership.objects.create(team=team, user=self.request.user, role=TeamMembership.Role.OWNER)

    def check_management(self, team):
        if not is_admin(team, self.request.user):
            raise PermissionDenied('Apenas administradores podem executar esta ação.')

    def perform_update(self, serializer):
        self.check_management(serializer.instance)
        serializer.save()

    def perform_destroy(self, instance):
        if instance.owner_id != self.request.user.pk:
            raise PermissionDenied('Somente o dono pode excluir a equipe.')
        instance.delete()

    @action(detail=False, methods=['get'], url_path='descobrir')
    def discover(self, request):
        term = request.query_params.get('search', '').strip()
        qs = Team.objects.none()
        if len(term) >= 2:
            qs = Team.objects.filter(name__icontains=term).order_by('id')
        page = self.paginate_queryset(qs)
        data = TeamDiscoverySerializer(page or [], many=True, context={'request': request}).data
        if page is not None:
            return self.get_paginated_response(data)
        return Response(data)

    @action(detail=True, methods=['get'], url_path='membros')
    def members(self, request, pk=None):
        team = self.get_object()
        qs = team.memberships.select_related('user').order_by('id')
        return Response(TeamMembershipSerializer(qs, many=True).data)

    @action(detail=True, methods=['get', 'post'], url_path='jogadores')
    def players(self, request, pk=None):
        team = self.get_object()
        if request.method == 'GET':
            return Response(PlayerSerializer(team.players.order_by('id'), many=True).data)
        self.check_management(team)
        serializer = PlayerSerializer(data=request.data, context={'team': team, 'request': request})
        serializer.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                serializer.save(team=team)
        except IntegrityError as exc:
            raise ValidationError({'detail': 'Jogador ou número já registrado.'}) from exc
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='convidar')
    def invite(self, request, pk=None):
        team = self.get_object()
        self.check_management(team)
        user_id = request.data.get('user_id')
        if not str(user_id or '').isdigit():
            raise ValidationError({'user_id': 'Informe um usuário válido.'})
        invitee = get_object_or_404(User, pk=user_id, is_active=True)
        if TeamMembership.objects.filter(team=team, user=invitee).exists():
            raise ValidationError({'user_id': 'Usuário já participa da equipe.'})
        if TeamInvitation.objects.filter(
            team=team,
            invitee=invitee,
            status=TeamInvitation.Status.PENDING,
        ).exists():
            raise ValidationError({'user_id': 'Já existe um convite pendente.'})
        try:
            with transaction.atomic():
                invite = TeamInvitation.objects.create(team=team, invitee=invitee, invited_by=request.user)
        except IntegrityError as exc:
            raise ValidationError({'detail': 'Já existe convite pendente.'}) from exc
        notify_user(
            invitee,
            'team_invitation',
            'Você recebeu um convite de equipe.',
            f'/convites',
            key=f'team-invite:{invite.pk}',
        )
        return Response(TeamInvitationSerializer(invite).data, status=status.HTTP_201_CREATED)


class TeamInvitationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TeamInvitationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            TeamInvitation.objects
            .filter(
                Q(invitee=self.request.user)
                | Q(team__memberships__user=self.request.user, team__memberships__role__in=['owner', 'admin'])
            )
            .distinct()
            .select_related('team')
            .order_by('-created_at')
        )

    @action(detail=True, methods=['post'], url_path='aceitar')
    def accept(self, request, pk=None):
        with transaction.atomic():
            invite = get_object_or_404(TeamInvitation.objects.select_for_update(), pk=pk, invitee=request.user)
            if invite.status != TeamInvitation.Status.PENDING:
                raise ValidationError({'detail': 'Convite não está pendente.'})
            if invite.expires_at <= timezone.now():
                invite.status = TeamInvitation.Status.EXPIRED
                invite.save(update_fields=['status'])
                expired = True
            else:
                TeamMembership.objects.get_or_create(
                    team=invite.team,
                    user=request.user,
                    defaults={'role': TeamMembership.Role.MEMBER},
                )
                invite.status = TeamInvitation.Status.ACCEPTED
                invite.save(update_fields=['status'])
                expired = False
        if expired:
            raise ValidationError({'detail': 'Convite expirado.'})
        return Response(TeamInvitationSerializer(invite).data)

    @action(detail=True, methods=['post'], url_path='recusar')
    def decline(self, request, pk=None):
        with transaction.atomic():
            invite = get_object_or_404(TeamInvitation.objects.select_for_update(), pk=pk, invitee=request.user)
            if invite.status != TeamInvitation.Status.PENDING:
                raise ValidationError({'detail': 'Convite não está pendente.'})
            invite.status = TeamInvitation.Status.DECLINED
            invite.save(update_fields=['status'])
        return Response(TeamInvitationSerializer(invite).data)
