"""Notificações internas de lembrete geradas uma única vez por usuário."""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Match, TeamMembership
from core.services.notifications import notify_user


class Command(BaseCommand):
    help = 'Cria lembretes internos para partidas do dia seguinte.'

    def handle(self, *args, **options):
        tomorrow = timezone.localdate() + timedelta(days=1)
        count = 0
        matches = Match.objects.filter(
            starts_at__date=tomorrow,
            status=Match.Status.SCHEDULED,
        ).select_related('team')
        for match in matches:
            for membership in TeamMembership.objects.filter(team=match.team).select_related('user'):
                notify_user(
                    membership.user,
                    'match_reminder',
                    'Você tem uma partida amanhã.',
                    '/partidas',
                    key=f'match-reminder:{match.pk}:{membership.user_id}',
                )
                count += 1
        self.stdout.write(self.style.SUCCESS(f'Lembretes processados: {count}'))
