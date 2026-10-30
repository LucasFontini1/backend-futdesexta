"""Eventos restritos aos membros da equipe e controle de presença."""

from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import EventAttendance, Team, TeamEvent
from core.serializers.event import EventAttendanceSerializer, TeamEventSerializer
from core.services.notifications import notify_team
from core.views.team import is_admin


class TeamEventViewSet(viewsets.ModelViewSet):
    serializer_class = TeamEventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TeamEvent.objects.filter(team__memberships__user=self.request.user).distinct().order_by('starts_at')

    def perform_create(self, serializer):
        team = get_object_or_404(Team, pk=self.request.data.get('team'))
        if not is_admin(team, self.request.user):
            raise PermissionDenied('Somente administradores criam eventos.')
        event = serializer.save(organizer=self.request.user, team=team)
        notify_team(team, 'event', 'Novo evento da equipe.', '/eventos', key=f'event:{event.pk}')

    def perform_update(self, serializer):
        if not is_admin(serializer.instance.team, self.request.user):
            raise PermissionDenied('Somente administradores editam eventos.')
        serializer.save()

    def perform_destroy(self, instance):
        if not is_admin(instance.team, self.request.user):
            raise PermissionDenied('Somente administradores excluem eventos.')
        instance.delete()

    @action(detail=True, methods=['get', 'post'], url_path='presenca')
    def attendance(self, request, pk=None):
        event = self.get_object()
        if request.method == 'GET':
            return Response(EventAttendanceSerializer(event.attendances.all(), many=True).data)
        serializer = EventAttendanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        EventAttendance.objects.update_or_create(
            event=event,
            user=request.user,
            defaults={'response': serializer.validated_data['response']},
        )
        return Response({'response': serializer.validated_data['response']})
