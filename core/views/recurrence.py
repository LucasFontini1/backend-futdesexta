"""API de recorrência com permissões administrativas."""

from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import RecurrenceRule, Team
from core.serializers.recurrence import RecurrenceRuleSerializer
from core.services.recurrence import generate_occurrences
from core.views.team import is_admin


class RecurrenceViewSet(viewsets.ModelViewSet):
    serializer_class = RecurrenceRuleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RecurrenceRule.objects.filter(team__memberships__user=self.request.user).distinct().order_by('id')

    def perform_create(self, serializer):
        team = get_object_or_404(Team, pk=self.request.data.get('team'))
        if not is_admin(team, self.request.user):
            raise PermissionDenied('Apenas administradores criam recorrências.')
        rule = serializer.save(team=team, created_by=self.request.user)
        generate_occurrences(rule)

    def perform_update(self, serializer):
        if not is_admin(serializer.instance.team, self.request.user):
            raise PermissionDenied('Apenas administradores editam recorrências.')
        serializer.save()

    def perform_destroy(self, instance):
        if not is_admin(instance.team, self.request.user):
            raise PermissionDenied('Apenas administradores encerram recorrências.')
        instance.active = False
        instance.save(update_fields=['active'])

    @action(detail=True, methods=['post'], url_path='gerar')
    def generate(self, request, pk=None):
        rule = self.get_object()
        if not is_admin(rule.team, request.user):
            raise PermissionDenied('Apenas administradores geram ocorrências.')
        return Response({'created': generate_occurrences(rule)})
