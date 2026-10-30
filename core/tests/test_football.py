"""Suíte funcional de escalações, resultados e rankings."""
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from core.models import (
    GoalEvent, Match, MatchResult, MatchSide, Player, ResultRevision, Team, TeamMembership, User,
)


class FootballResultTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('fo-owner@example.com', 'password12345')
        self.member = User.objects.create_user('fo-member@example.com', 'password12345')
        self.outsider = User.objects.create_user('fo-guest@example.com', 'password12345')
        self.team = Team.objects.create(name='União', owner=self.owner)
        TeamMembership.objects.create(team=self.team, user=self.owner, role='owner')
        TeamMembership.objects.create(team=self.team, user=self.member, role='member')
        self.player1 = Player.objects.create(team=self.team, name='João', shirt_number=9)
        self.player2 = Player.objects.create(team=self.team, name='Maria', shirt_number=1)
        start = timezone.now() + timedelta(days=1)
        self.match = Match.objects.create(
            team=self.team, title='Pelada de sexta',
            starts_at=start, ends_at=start + timedelta(hours=1),
        )
        self.client = APIClient()
        self.client.force_authenticate(self.owner)
        self.home = MatchSide.objects.create(match=self.match, name='Verde', order=1)
        self.away = MatchSide.objects.create(match=self.match, name='Preto', order=2)
        self.url = f'/api/partidas/{self.match.pk}/'

    def test_manual_lineup_prevents_duplicate_player(self):
        duplicates = [
            {'side': self.home.pk, 'player': self.player1.pk},
            {'side': self.away.pk, 'player': self.player1.pk},
        ]
        response = self.client.put(self.url + 'escalacao/', {'slots': duplicates}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_result_corrects_without_double_counting(self):
        slots = [
            {'side': self.home.pk, 'player': self.player1.pk, 'position': 'Atacante'},
            {'side': self.away.pk, 'player': self.player2.pk, 'goalkeeper': True},
        ]
        self.assertEqual(
            self.client.put(self.url + 'escalacao/', {'slots': slots}, format='json').status_code, 200
        )
        data = {
            'home_side': self.home.pk, 'away_side': self.away.pk,
            'home_score': 2, 'away_score': 0,
            'goals': [{
                'scoring_side': self.home.pk, 'scorer': self.player1.pk,
                'conceded_by': self.player2.pk,
            }],
        }
        self.assertEqual(self.client.post(self.url + 'resultado/', data, format='json').status_code, 200)
        self.assertEqual(self.client.post(self.url + 'resultado/', data, format='json').status_code, 200)
        self.assertEqual(MatchResult.objects.filter(match=self.match).count(), 1)
        self.assertEqual(GoalEvent.objects.count(), 1)
        self.assertEqual(ResultRevision.objects.count(), 2)
        response = self.client.get('/api/estatisticas/?kind=pelada')
        self.assertEqual(response.status_code, 200)
        player_stats = next(x for x in response.data['ranking'] if x['player'] == self.player1.pk)
        self.assertEqual(player_stats['games'], 1)
        self.assertEqual(player_stats['goals'], 1)
        self.assertEqual(player_stats['wins'], 1)
        all_response = self.client.get('/api/estatisticas/?kind=geral')
        all_stats = next(x for x in all_response.data['ranking'] if x['player'] == self.player1.pk)
        self.assertEqual(all_stats['games'], player_stats['games'])

    def test_members_cannot_modify_result(self):
        self.client.force_authenticate(self.member)
        data = {'home_side': self.home.pk, 'away_side': self.away.pk, 'home_score': 1, 'away_score': 1}
        self.assertEqual(self.client.post(self.url + 'resultado/', data).status_code, 403)

    def test_outsiders_cannot_get_lineup_or_stats(self):
        self.client.force_authenticate(self.outsider)
        self.assertEqual(self.client.get(self.url + 'escalacao/').status_code, 404)
        self.assertEqual(self.client.get(self.url + 'resultado/').status_code, 404)
        self.assertEqual(self.client.get('/api/estatisticas/').data['ranking'], [])

    def test_result_must_match_its_sides(self):
        data = {'home_side': self.home.pk, 'away_side': self.home.pk, 'home_score': 1, 'away_score': 2}
        self.assertEqual(self.client.post(self.url + 'resultado/', data, format='json').status_code, 400)
