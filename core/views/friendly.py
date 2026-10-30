"""Aceitação de amistosos e validação compartilhada dos resultados."""

from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import FriendlyInvitation, Match, MatchSide
from core.serializers.friendly import FriendlyInvitationSerializer
from core.services.notifications import notify_team
from core.services.schedule import assert_teams_available
from core.views.team import is_admin


class FriendlyViewSet(viewsets.ModelViewSet):
    serializer_class = FriendlyInvitationSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        return (
            FriendlyInvitation.objects
            .filter(Q(from_team__memberships__user=self.request.user) | Q(to_team__memberships__user=self.request.user))
            .distinct()
            .order_by('-created_at')
        )

    def perform_create(self, serializer):
        from_team = serializer.validated_data['from_team']
        if not is_admin(from_team, self.request.user):
            raise PermissionDenied('Somente administradores convidam para amistosos.')
        invitation = serializer.save(invited_by=self.request.user)
        notify_team(
            invitation.to_team,
            'friendly_invitation',
            'Sua equipe recebeu um convite de amistoso.',
            '/amistosos',
            key=f'friendly:{invitation.pk}',
        )

    @action(detail=True, methods=['post'], url_path='responder')
    def respond(self, request, pk=None):
        invitation = self.get_object()
        if not is_admin(invitation.to_team, request.user):
            raise PermissionDenied('Somente administradores da equipe convidada respondem.')
        decision = request.data.get('accept')
        if not isinstance(decision, bool):
            raise ValidationError({'accept': 'Informe true ou false.'})
        with transaction.atomic():
            invitation = FriendlyInvitation.objects.select_for_update().get(pk=invitation.pk)
            if invitation.status != FriendlyInvitation.Status.PENDING:
                raise ValidationError('Convite já respondido.')
            if decision:
                assert_teams_available(
                    [invitation.from_team_id, invitation.to_team_id],
                    invitation.starts_at, invitation.ends_at,
                )
                # Uma partida oficial, compartilhada entre equipes.
                match = Match.objects.create(
                    team=invitation.from_team,
                    title='Amistoso',
                    kind=Match.Kind.FRIENDLY,
                    starts_at=invitation.starts_at,
                    ends_at=invitation.ends_at,
                    location=invitation.location,
                )
                MatchSide.objects.create(
                    match=match, team=invitation.from_team, name=invitation.from_team.name, order=1
                )
                MatchSide.objects.create(match=match, team=invitation.to_team, name=invitation.to_team.name, order=2)
                invitation.match = match
                invitation.status = FriendlyInvitation.Status.ACCEPTED
            else:
                invitation.status = FriendlyInvitation.Status.DECLINED
            invitation.save()
        notify_team(
            invitation.from_team,
            'friendly_response',
            'O convite de amistoso recebeu uma resposta.',
            '/amistosos',
            key=f'friendly-response:{invitation.pk}',
        )
        return Response(self.get_serializer(invitation).data)

    @action(detail=True, methods=['post'], url_path='aprovar-resultado')
    def approve_result(self, request, pk=None):
        invitation = self.get_object()
        if invitation.status != FriendlyInvitation.Status.ACCEPTED or not invitation.match_id:
            raise ValidationError('Amistoso não aceito.')
        if not hasattr(invitation.match, 'result'):
            raise ValidationError('Registre o placar antes de aprová-lo.')
        from_admin = is_admin(invitation.from_team, request.user)
        to_admin = is_admin(invitation.to_team, request.user)
        if not (from_admin or to_admin):
            raise PermissionDenied('Somente administradores das duas equipes aprovam.')
        with transaction.atomic():
            invitation = FriendlyInvitation.objects.select_for_update().get(pk=invitation.pk)
            if from_admin:
                invitation.result_approved_from = True
            if to_admin:
                invitation.result_approved_to = True
            invitation.save(update_fields=['result_approved_from', 'result_approved_to'])
            if invitation.result_approved_from and invitation.result_approved_to:
                Match.objects.filter(pk=invitation.match_id).update(status=Match.Status.FINISHED)
        return Response(self.get_serializer(invitation).data)
