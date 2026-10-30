"""Calendário unificado com isolamento dos dados de cada equipe."""
from datetime import date, timedelta
from django.db.models import Q
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from core.models import Match, TeamEvent


class CalendarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        begin = request.query_params.get('start')
        end = request.query_params.get('end')
        try:
            start_day = date.fromisoformat(begin) if begin else timezone.localdate()
            end_day = date.fromisoformat(end) if end else start_day + timedelta(days=45)
        except ValueError:
            return Response({'detail': 'Datas inválidas.'}, status=400)
        if end_day < start_day or (end_day - start_day).days > 366:
            return Response({'detail': 'Intervalo limitado a um ano.'}, status=400)
        matches = Match.objects.filter(
            Q(team__memberships__user=request.user) |
            Q(sides__team__memberships__user=request.user) |
            Q(competition_fixture__competition__owner=request.user) |
            Q(competition_fixture__competition__administrators__user=request.user),
            starts_at__date__gte=start_day, starts_at__date__lte=end_day,
        ).distinct().order_by('starts_at')
        events = TeamEvent.objects.filter(
            team__memberships__user=request.user,
            starts_at__date__gte=start_day, starts_at__date__lte=end_day,
        ).distinct().order_by('starts_at')
        items = [
            {
                'id': match.id, 'type': match.kind, 'title': match.title,
                'start': match.starts_at, 'end': match.ends_at,
                'location': match.location, 'status': match.status,
                'link': f'/partidas/{match.id}',
            }
            for match in matches
        ]
        items.extend({
            'id': event.id, 'type': 'event', 'title': event.title,
            'start': event.starts_at, 'end': event.ends_at,
            'location': event.location, 'status': 'scheduled',
            'link': '/eventos',
        } for event in events)
        items.sort(key=lambda item: item['start'])
        return Response(items)
