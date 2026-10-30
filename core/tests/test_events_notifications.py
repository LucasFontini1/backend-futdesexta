"""Privacidade da central de notificações e dos eventos internos."""

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from core.models import Notification, Team, TeamMembership, User


class EventNotificationTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user('event-admin@example.com', 'samplepassword123')
        self.other = User.objects.create_user('event-other@example.com', 'samplepassword123')
        self.team = Team.objects.create(name='Equipe Fechada', owner=self.admin)
        TeamMembership.objects.create(team=self.team, user=self.admin, role='owner')
        self.client = APIClient()
        self.client.force_authenticate(self.admin)

    def test_event_and_notification_are_private(self):
        start = timezone.now() + timedelta(days=3)
        response = self.client.post(
            '/api/eventos/',
            {
                'team': self.team.pk,
                'title': 'Churrasco',
                'starts_at': start.isoformat(),
                'ends_at': (start + timedelta(hours=2)).isoformat(),
            },
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertGreater(Notification.objects.filter(user=self.admin).count(), 0)
        event_id = response.data['id']
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get(f'/api/eventos/{event_id}/').status_code, 404)
        self.assertEqual(self.client.get('/api/notificacoes/').data['results'], [])
        self.assertEqual(
            self.client.post(
                '/api/eventos/',
                {
                    'team': self.team.pk,
                    'title': 'Hacker',
                    'starts_at': start.isoformat(),
                    'ends_at': (start + timedelta(hours=1)).isoformat(),
                },
            ).status_code,
            403,
        )
