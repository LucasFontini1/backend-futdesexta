"""Atualiza ocorrências recorrentes da temporada."""

from django.core.management.base import BaseCommand

from core.models import RecurrenceRule
from core.services.recurrence import generate_occurrences


class Command(BaseCommand):
    help = 'Gera as próximas ocorrências de peladas recorrentes.'

    def add_arguments(self, parser):
        parser.add_argument('--weeks', type=int, default=8)

    def handle(self, *args, **options):
        count = sum(
            generate_occurrences(rule, options['weeks'])
            for rule in RecurrenceRule.objects.filter(active=True).select_related('team')
        )
        self.stdout.write(self.style.SUCCESS(f'Partidas geradas: {count}'))
