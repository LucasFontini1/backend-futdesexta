"""Testes de geração idempotente e permissão das peladas semanais."""

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from core.models import Match, RecurrenceRule, Team, TeamMembership, User
from core.services.recurrence import generate_occurrences


class RecurrenceTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('rec-owner@example.com', 'samplepassword123')
        self.stranger = User.objects.create_user('rec-guest@example.com', 'samplepassword123')
        self.team = Team.objects.create(name='Recorrente', owner=self.owner)
        TeamMembership.objects.create(team=self.team, user=self.owner, role='owner')
        self.client = APIClient()
        self.client.force_authenticate(self.owner)

    def test_generating_twice_never_duplicates_match(self):
        today = timezone.localdate() + timedelta(days=1)
        rule = RecurrenceRule.objects.create(
            team=self.team,
            title='Toda semana',
            starts_on=today,
            weekday=today.weekday(),
            start_time='19:00',
            end_time='21:00',
            created_by=self.owner,
        )
        first = generate_occurrences(rule, weeks=4)
        self.assertGreater(first, 0)
        self.assertEqual(generate_occurrences(rule, weeks=4), 0)
        self.assertEqual(Match.objects.filter(team=self.team).count(), first)

    def test_outsider_cannot_create_series(self):
        tomorrow = timezone.localdate() + timedelta(days=1)
        self.client.force_authenticate(self.stranger)
        response = self.client.post(
            '/api/recorrencias/',
            {
                'team': self.team.pk,
                'title': 'Inválida',
                'weekday': tomorrow.weekday(),
                'starts_on': tomorrow.isoformat(),
                'start_time': '19:00',
                'end_time': '21:00',
            },
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(RecurrenceRule.objects.count(), 0)
