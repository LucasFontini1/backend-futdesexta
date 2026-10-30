"""Ações administrativas de equipe e vínculos de jogadores."""
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from core.models import Player, PlayerLinkRequest, Team, TeamMembership
from core.serializers.team import PlayerSerializer, TeamMembershipSerializer, TeamSerializer


class TeamManagementActions:
    def require_admin(self, team, user):
        if not TeamMembership.objects.filter(
            team=team, user=user, role__in=['owner', 'admin']
        ).exists():
            raise PermissionDenied('Somente administradores.')

    @action(detail=True, methods=['post'], url_path='alterar-papel')
    def change_role(self, request, pk=None):
        team = self.get_object()
        if team.owner_id != request.user.pk:
            raise PermissionDenied('Somente o dono altera os papéis.')
        member = get_object_or_404(TeamMembership, team=team, user_id=request.data.get('user_id'))
        if member.user_id == team.owner_id:
            raise ValidationError('O papel do dono não pode ser alterado.')
        role = request.data.get('role')
        if role not in ['member', 'admin']:
            raise ValidationError('Escolha admin ou member.')
        member.role = role
        member.save(update_fields=['role'])
        return Response(TeamMembershipSerializer(member).data)

    @action(detail=True, methods=['post'], url_path='transferir-propriedade')
    def transfer_ownership(self, request, pk=None):
        team = self.get_object()
        if team.owner_id != request.user.pk:
            raise PermissionDenied('Somente o dono transfere a equipe.')
        with transaction.atomic():
            team = Team.objects.select_for_update().get(pk=team.pk)
            member = get_object_or_404(TeamMembership, team=team, user_id=request.data.get('user_id'))
            if member.user_id == team.owner_id:
                raise ValidationError('Esta pessoa já é dona.')
            TeamMembership.objects.filter(team=team, user=team.owner).update(role='admin')
            member.role = TeamMembership.Role.OWNER
            member.save(update_fields=['role'])
            team.owner = member.user
            team.save(update_fields=['owner'])
        return Response(TeamSerializer(team).data)

    @action(detail=True, methods=['post'], url_path='criar-meu-jogador')
    def create_my_player(self, request, pk=None):
        team = self.get_object()
        if Player.objects.filter(team=team, linked_user=request.user).exists():
            raise ValidationError('Sua conta já tem um jogador nesta equipe.')
        serializer = PlayerSerializer(data=request.data, context={'team': team, 'request': request})
        serializer.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                serializer.save(team=team, linked_user=request.user)
        except IntegrityError as exc:
            raise ValidationError('Jogador ou número já cadastrado.') from exc
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='solicitar-vinculo')
    def request_link(self, request, pk=None):
        team = self.get_object()
        player = get_object_or_404(Player, team=team, pk=request.data.get('player_id'))
        if player.linked_user_id:
            raise ValidationError('Jogador já possui conta vinculada.')
        if Player.objects.filter(team=team, linked_user=request.user).exists():
            raise ValidationError('Você já possui jogador vinculado.')
        if PlayerLinkRequest.objects.filter(player=player, user=request.user, status='pending').exists():
            raise ValidationError('Já existe solicitação pendente.')
        link = PlayerLinkRequest.objects.create(player=player, user=request.user)
        return Response({'id': link.pk, 'status': link.status}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get', 'post'], url_path='vinculos-pendentes')
    def review_links(self, request, pk=None):
        team = self.get_object()
        self.require_admin(team, request.user)
        if request.method == 'GET':
            return Response(list(PlayerLinkRequest.objects.filter(
                player__team=team, status='pending'
            ).values('id', 'player_id', 'user_id', 'status')))
        choice = request.data.get('approve')
        if not isinstance(choice, bool):
            raise ValidationError('Informe approve como true ou false.')
        with transaction.atomic():
            link = get_object_or_404(
                PlayerLinkRequest.objects.select_for_update(), pk=request.data.get('request_id'),
                player__team=team, status='pending',
            )
            player = Player.objects.select_for_update().get(pk=link.player_id)
            if choice:
                if player.linked_user_id or Player.objects.filter(team=team, linked_user=link.user).exists():
                    raise ValidationError('Vínculo duplicado ou jogador já associado.')
                player.linked_user = link.user
                player.save(update_fields=['linked_user'])
            link.status = 'approved' if choice else 'rejected'
            link.save(update_fields=['status'])
        return Response({'status': link.status})

    @action(detail=True, methods=['delete'], url_path=r'membros/(?P<user_id>[^/.]+)')
    def remove_member(self, request, pk=None, user_id=None):
        team = self.get_object()
        self.require_admin(team, request.user)
        member = get_object_or_404(TeamMembership, team=team, user_id=user_id)
        if member.user_id == team.owner_id:
            raise ValidationError('Transfira a propriedade antes de remover o dono.')
        member.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
