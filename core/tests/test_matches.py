"""Testa peladas e presença, incluindo autorização por equipe."""
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from core.models import Match, MatchAttendance, Team, TeamMembership, User


class MatchSecurityTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('owner2@example.com', 'pass123456')
        self.member = User.objects.create_user('member2@example.com', 'pass123456')
        self.outsider = User.objects.create_user('stranger2@example.com', 'pass123456')
        self.team = Team.objects.create(name='Equipe 1', owner=self.owner)
        TeamMembership.objects.create(team=self.team, user=self.owner, role='owner')
        TeamMembership.objects.create(team=self.team, user=self.member, role='member')
        self.client = APIClient()
        self.client.force_authenticate(self.owner)
        self.start = timezone.now() + timedelta(days=2)
        self.end = self.start + timedelta(hours=2)
        self.payload = {
            'team': self.team.pk, 'title': 'Sexta à noite',
            'starts_at': self.start.isoformat(), 'ends_at': self.end.isoformat(),
        }

    def test_only_admin_creates_and_updates(self):
        created = self.client.post('/api/partidas/', self.payload, format='json')
        self.assertEqual(created.status_code, 201)
        match_id = created.data['id']
        self.assertEqual(Match.objects.get(pk=match_id).kind, 'pelada')
        self.client.force_authenticate(self.member)
        self.assertEqual(self.client.post('/api/partidas/', self.payload, format='json').status_code, 403)
        self.assertEqual(self.client.patch(f'/api/partidas/{match_id}/', {'title': 'Alterada'}).status_code, 403)

    def test_outsider_cannot_read_or_answer(self):
        match = Match.objects.create(
            team=self.team, title='Sexta', starts_at=self.start, ends_at=self.end
        )
        self.client.force_authenticate(self.outsider)
        self.assertEqual(self.client.get(f'/api/partidas/{match.id}/').status_code, 404)
        self.assertEqual(
            self.client.post(f'/api/partidas/{match.id}/presenca/', {'response': 'going'}).status_code,
            404,
        )

    def test_member_can_only_choose_going_or_not_going(self):
        match = Match.objects.create(
            team=self.team, title='Sexta', starts_at=self.start, ends_at=self.end
        )
        self.client.force_authenticate(self.member)
        url = f'/api/partidas/{match.id}/presenca/'
        self.assertEqual(self.client.post(url, {'response': 'maybe'}).status_code, 400)
        self.assertEqual(self.client.post(url, {'response': 'going'}).status_code, 200)
        self.assertEqual(self.client.post(url, {'response': 'not_going'}).status_code, 200)
        self.assertEqual(MatchAttendance.objects.filter(match=match, user=self.member).count(), 1)
        self.assertEqual(MatchAttendance.objects.get(match=match, user=self.member).response, 'not_going')

    def test_cannot_answer_canceled_or_started_matches(self):
        match = Match.objects.create(
            team=self.team, title='Cancelada', starts_at=self.start, ends_at=self.end,
            status=Match.Status.CANCELED,
        )
        self.client.force_authenticate(self.member)
        self.assertEqual(
            self.client.post(f'/api/partidas/{match.id}/presenca/', {'response': 'going'}).status_code,
            400,
        )

    def test_rejects_invalid_date_order(self):
        payload = {**self.payload, 'ends_at': (self.start - timedelta(hours=1)).isoformat()}
        self.assertEqual(self.client.post('/api/partidas/', payload, format='json').status_code, 400)
