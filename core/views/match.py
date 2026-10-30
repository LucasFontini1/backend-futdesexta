"""Criação de peladas e confirmação de presença protegidas por equipe."""
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.models import Match, MatchAttendance, Team
from core.serializers import AttendanceSerializer, MatchSerializer
from core.views.team import is_admin


class MatchViewSet(viewsets.ModelViewSet):
    serializer_class = MatchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Match.objects.filter(
            team__memberships__user=self.request.user
        ).select_related('team').distinct().order_by('starts_at')

    def perform_create(self, serializer):
        team = get_object_or_404(Team, pk=self.request.data.get('team'))
        if not is_admin(team, self.request.user):
            raise PermissionDenied('Somente administradores criam peladas.')
        serializer.save(team=team, kind=Match.Kind.PELADA)

    def perform_update(self, serializer):
        if not is_admin(serializer.instance.team, self.request.user):
            raise PermissionDenied('Somente administradores editam partidas.')
        serializer.save()

    def perform_destroy(self, instance):
        if not is_admin(instance.team, self.request.user):
            raise PermissionDenied('Somente administradores excluem partidas.')
        if instance.status == Match.Status.FINISHED:
            raise ValidationError({'detail': 'Partidas realizadas devem preservar o histórico.'})
        instance.delete()

    @action(detail=True, methods=['get', 'post'], url_path='presenca')
    def attendance(self, request, pk=None):
        match = self.get_object()
        if request.method == 'GET':
            records = match.attendances.select_related('user').order_by('id')
            return Response(AttendanceSerializer(records, many=True).data)
        if match.status != Match.Status.SCHEDULED or timezone.now() >= match.starts_at:
            raise ValidationError({'detail': 'O prazo de confirmação terminou.'})
        data = AttendanceSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        record, _ = MatchAttendance.objects.update_or_create(
            match=match, user=request.user,
            defaults={'response': data.validated_data['response']},
        )
        return Response(AttendanceSerializer(record).data, status=status.HTTP_200_OK)
