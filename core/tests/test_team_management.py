"""Permissões de propriedade e vínculo de jogadores pré-cadastrados."""

from django.test import TestCase
from rest_framework.test import APIClient

from core.models import Player, Team, TeamMembership, User


class TeamManagementTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('transfer-owner@example.com', 'password12345')
        self.member = User.objects.create_user('transfer-member@example.com', 'password12345')
        self.guest = User.objects.create_user('transfer-guest@example.com', 'password12345')
        self.team = Team.objects.create(name='Transferir', owner=self.owner)
        TeamMembership.objects.create(team=self.team, user=self.owner, role='owner')
        TeamMembership.objects.create(team=self.team, user=self.member, role='member')
        self.player = Player.objects.create(team=self.team, name='Antigo camisa 10', shirt_number=10)
        self.client = APIClient()

    def test_only_owner_can_transfer_team(self):
        url = f'/api/equipes/{self.team.pk}/transferir-propriedade/'
        self.client.force_authenticate(self.member)
        self.assertEqual(self.client.post(url, {'user_id': self.member.pk}).status_code, 403)
        self.client.force_authenticate(self.owner)
        self.assertEqual(self.client.post(url, {'user_id': self.member.pk}).status_code, 200)
        self.team.refresh_from_db()
        self.assertEqual(self.team.owner_id, self.member.pk)

    def test_player_link_needs_admin_approval(self):
        self.client.force_authenticate(self.member)
        response = self.client.post(
            f'/api/equipes/{self.team.pk}/solicitar-vinculo/',
            {'player_id': self.player.pk},
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.player.refresh_from_db()
        self.assertIsNone(self.player.linked_user_id)
        self.client.force_authenticate(self.guest)
        self.assertEqual(self.client.get(f'/api/equipes/{self.team.pk}/vinculos-pendentes/').status_code, 404)
        self.client.force_authenticate(self.owner)
        approved = self.client.post(
            f'/api/equipes/{self.team.pk}/vinculos-pendentes/',
            {'request_id': response.data['id'], 'approve': True},
            format='json',
        )
        self.assertEqual(approved.status_code, 200)
        self.player.refresh_from_db()
        self.assertEqual(self.player.linked_user_id, self.member.pk)
