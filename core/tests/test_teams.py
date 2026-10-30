"""Testes de autorização e fluxo de equipes privadas."""
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from core.models import Team, TeamInvitation, TeamMembership, User


class PrivateTeamsTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('owner@example.com', 'safe-pass-123', username='owner')
        self.member = User.objects.create_user('member@example.com', 'safe-pass-123', username='member')
        self.outsider = User.objects.create_user('outside@example.com', 'safe-pass-123', username='outsider')
        self.client = APIClient()
        self.client.force_authenticate(self.owner)

    def test_only_owner_and_invited_members_can_access_private_team(self):
        created = self.client.post('/api/equipes/', {'name': 'Sexta FC'}, format='json')
        self.assertEqual(created.status_code, 201)
        team_id = created.data['id']
        self.assertTrue(TeamMembership.objects.filter(
            team_id=team_id, user=self.owner, role='owner'
        ).exists())
        self.client.force_authenticate(self.outsider)
        self.assertEqual(self.client.get(f'/api/equipes/{team_id}/').status_code, 404)
        self.assertEqual(self.client.get(f'/api/equipes/{team_id}/membros/').status_code, 404)
        discovery = self.client.get('/api/equipes/descobrir/?search=Sexta')
        self.assertEqual(discovery.status_code, 200)
        self.assertNotIn('owner', str(discovery.data['results'][0]))
        self.assertNotIn('description', str(discovery.data['results'][0]))

    def test_invitation_requires_admin_and_recipient(self):
        team = Team.objects.create(name='Sexta', owner=self.owner)
        TeamMembership.objects.create(team=team, user=self.owner, role='owner')
        TeamMembership.objects.create(team=team, user=self.member, role='member')
        self.client.force_authenticate(self.member)
        denied = self.client.post(f'/api/equipes/{team.pk}/convidar/', {'user_id': self.outsider.pk})
        self.assertEqual(denied.status_code, 403)
        self.client.force_authenticate(self.owner)
        response = self.client.post(
            f'/api/equipes/{team.pk}/convidar/', {'user_id': self.outsider.pk}, format='json'
        )
        self.assertEqual(response.status_code, 201)
        invitation_id = response.data['id']
        duplicate = self.client.post(
            f'/api/equipes/{team.pk}/convidar/', {'user_id': self.outsider.pk}, format='json'
        )
        self.assertEqual(duplicate.status_code, 400)
        self.client.force_authenticate(self.member)
        self.assertEqual(
            self.client.post(f'/api/convites-equipe/{invitation_id}/aceitar/').status_code, 404
        )
        self.client.force_authenticate(self.outsider)
        self.assertEqual(
            self.client.post(f'/api/convites-equipe/{invitation_id}/aceitar/').status_code, 200
        )
        self.assertTrue(TeamMembership.objects.filter(team=team, user=self.outsider).exists())
        self.assertEqual(
            self.client.post(f'/api/convites-equipe/{invitation_id}/aceitar/').status_code, 400
        )

    def test_member_cannot_edit_team_or_create_player(self):
        team = Team.objects.create(name='Sexta', owner=self.owner)
        TeamMembership.objects.create(team=team, user=self.owner, role='owner')
        TeamMembership.objects.create(team=team, user=self.member, role='member')
        self.client.force_authenticate(self.member)
        self.assertEqual(
            self.client.patch(f'/api/equipes/{team.pk}/', {'name': 'Outra'}, format='json').status_code,
            403,
        )
        self.assertEqual(
            self.client.post(f'/api/equipes/{team.pk}/jogadores/', {'name': 'Teste'}).status_code,
            403,
        )

    def test_players_require_unique_shirt_number(self):
        team = Team.objects.create(name='Sexta', owner=self.owner)
        TeamMembership.objects.create(team=team, user=self.owner, role='owner')
        url = f'/api/equipes/{team.pk}/jogadores/'
        self.assertEqual(self.client.post(url, {'name': 'A', 'shirt_number': 10}).status_code, 201)
        self.assertEqual(self.client.post(url, {'name': 'B', 'shirt_number': 10}).status_code, 400)

    def test_search_never_returns_email_or_admin_fields(self):
        self.client.force_authenticate(self.outsider)
        response = self.client.get('/api/usuarios/?search=owner')
        self.assertEqual(response.status_code, 200)
        payload = str(response.data)
        self.assertNotIn('owner@example.com', payload)
        self.assertNotIn('is_superuser', payload)

    def test_expired_invite_never_joins_and_is_persisted(self):
        team = Team.objects.create(name='Sexta', owner=self.owner)
        TeamMembership.objects.create(team=team, user=self.owner, role='owner')
        invite = TeamInvitation.objects.create(
            team=team, invited_by=self.owner, invitee=self.outsider,
            expires_at=timezone.now() - timedelta(days=1),
        )
        self.client.force_authenticate(self.outsider)
        response = self.client.post(f'/api/convites-equipe/{invite.pk}/aceitar/')
        self.assertEqual(response.status_code, 400)
        invite.refresh_from_db()
        self.assertEqual(invite.status, 'expired')
        self.assertFalse(TeamMembership.objects.filter(team=team, user=self.outsider).exists())

    def test_unauthenticated_requests_are_denied(self):
        self.client.force_authenticate(user=None)
        self.assertIn(self.client.get('/api/equipes/').status_code, [401, 403])
        self.assertIn(self.client.get('/api/usuarios/?search=abc').status_code, [401, 403])
