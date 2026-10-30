"""Exercita convites entre equipes e proteção das competições."""

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from core.models import (
    CompetitionTeam,
    FriendlyInvitation,
    Match,
    Team,
    TeamMembership,
    User,
)


class InvitationsAndCompetitionsTest(TestCase):
    def setUp(self):
        self.a = User.objects.create_user('friendly-a@example.com', 'samplepassword123')
        self.b = User.objects.create_user('friendly-b@example.com', 'samplepassword123')
        self.guest = User.objects.create_user('friendly-guest@example.com', 'samplepassword123')
        self.ta = Team.objects.create(name='Time A', owner=self.a)
        self.tb = Team.objects.create(name='Time B', owner=self.b)
        TeamMembership.objects.create(team=self.ta, user=self.a, role='owner')
        TeamMembership.objects.create(team=self.tb, user=self.b, role='owner')
        self.client = APIClient()
        self.start = timezone.now() + timedelta(days=4)
        self.end = self.start + timedelta(hours=2)

    def test_friendly_needs_invited_teams_admin(self):
        self.client.force_authenticate(self.a)
        invite = self.client.post(
            '/api/amistosos/',
            {
                'from_team': self.ta.pk,
                'to_team': self.tb.pk,
                'starts_at': self.start.isoformat(),
                'ends_at': self.end.isoformat(),
            },
            format='json',
        )
        self.assertEqual(invite.status_code, 201)
        self.client.force_authenticate(self.guest)
        self.assertEqual(self.client.get('/api/amistosos/').data['results'], [])
        self.assertEqual(
            self.client.post(
                f'/api/amistosos/{invite.data["id"]}/responder/', {'accept': True}, format='json'
            ).status_code,
            404,
        )
        self.client.force_authenticate(self.b)
        accepted = self.client.post(f'/api/amistosos/{invite.data["id"]}/responder/', {'accept': True}, format='json')
        self.assertEqual(accepted.status_code, 200)
        self.assertEqual(Match.objects.filter(kind='friendly').count(), 1)
        self.assertEqual(FriendlyInvitation.objects.get(pk=invite.data['id']).status, 'accepted')

    def test_only_existing_registered_teams_can_participate(self):
        self.client.force_authenticate(self.a)
        comp = self.client.post('/api/competicoes/', {'name': 'Campeonato', 'format': 'league'}, format='json')
        self.assertEqual(comp.status_code, 201)
        competition_id = comp.data['id']
        invalid = self.client.post(f'/api/competicoes/{competition_id}/convidar/', {'team': 999999}, format='json')
        self.assertEqual(invalid.status_code, 404)
        invite = self.client.post(f'/api/competicoes/{competition_id}/convidar/', {'team': self.tb.pk}, format='json')
        self.assertEqual(invite.status_code, 201)
        self.client.force_authenticate(self.guest)
        self.assertEqual(
            self.client.post(
                f'/api/convites-competicao/{invite.data["id"]}/responder/', {'accept': True}, format='json'
            ).status_code,
            404,
        )
        self.client.force_authenticate(self.b)
        response = self.client.post(
            f'/api/convites-competicao/{invite.data["id"]}/responder/', {'accept': True}, format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            CompetitionTeam.objects.filter(
                competition_id=competition_id,
                team=self.tb,
            ).exists()
        )
