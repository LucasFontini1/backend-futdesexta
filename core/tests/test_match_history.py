"""Histórico: filtro de partidas terminadas sem revelar equipes privadas."""

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from core.models import Match, Team, TeamMembership, User


class MatchHistoryTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('history-owner@example.com', 'SafePass-2026!')
        self.outsider = User.objects.create_user('history-outsider@example.com', 'SafePass-2026!')
        self.team = Team.objects.create(name='Equipe Privada', owner=self.owner)
        TeamMembership.objects.create(team=self.team, user=self.owner, role='owner')
        when = timezone.now() - timedelta(days=2)
        self.finished = Match.objects.create(
            team=self.team,
            title='Pelada realizada',
            status=Match.Status.FINISHED,
            kind=Match.Kind.PELADA,
            starts_at=when,
            ends_at=when + timedelta(hours=1),
        )
        self.scheduled = Match.objects.create(
            team=self.team,
            title='Pelada futura',
            status=Match.Status.SCHEDULED,
            starts_at=timezone.now() + timedelta(days=1),
            ends_at=timezone.now() + timedelta(days=1, hours=1),
        )
        self.client = APIClient()

    def test_filters_only_finished_matches(self):
        self.client.force_authenticate(self.owner)
        response = self.client.get('/api/partidas/?status=finished&kind=pelada')
        self.assertEqual(response.status_code, 200)
        ids = [item['id'] for item in response.data['results']]
        self.assertIn(self.finished.pk, ids)
        self.assertNotIn(self.scheduled.pk, ids)

    def test_external_user_cannot_discover_private_history(self):
        self.client.force_authenticate(self.outsider)
        response = self.client.get('/api/partidas/?status=finished')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'], [])

    def test_invalid_filter_is_rejected(self):
        self.client.force_authenticate(self.owner)
        self.assertEqual(self.client.get('/api/partidas/?status=inexistente').status_code, 400)
        self.assertEqual(self.client.get('/api/partidas/?kind=inexistente').status_code, 400)
