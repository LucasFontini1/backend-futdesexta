"""Regressões para métricas opcionais, autorização e total por modalidade."""

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from core.models import Match, MatchMetric, MatchSide, Player, Team, TeamMembership, User


class OptionalMetricsTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user('metric-owner@example.com', 'Password123!')
        self.member = User.objects.create_user('metric-member@example.com', 'Password123!')
        self.guest = User.objects.create_user('metric-guest@example.com', 'Password123!')
        self.team = Team.objects.create(name='Sexta Verde', owner=self.admin)
        TeamMembership.objects.create(team=self.team, user=self.admin, role='owner')
        TeamMembership.objects.create(team=self.team, user=self.member, role='member')
        self.player = Player.objects.create(team=self.team, name='Goleiro', shirt_number=1)
        self.reserve = Player.objects.create(team=self.team, name='Reserva', shirt_number=2)
        begin = timezone.now() + timedelta(days=2)
        self.match = Match.objects.create(
            team=self.team, title='Pelada', starts_at=begin, ends_at=begin + timedelta(hours=2)
        )
        home = MatchSide.objects.create(match=self.match, name='Casa', order=1)
        away = MatchSide.objects.create(match=self.match, name='Fora', order=2)
        self.client = APIClient()
        self.client.force_authenticate(self.admin)
        lineup = [
            {'side': home.pk, 'player': self.player.pk, 'goalkeeper': True},
            {'side': away.pk, 'player': self.reserve.pk, 'reserve': True},
        ]
        self.assertEqual(
            self.client.put(f'/api/partidas/{self.match.pk}/escalacao/', {'slots': lineup}, format='json').status_code,
            200,
        )
        self.assertEqual(
            self.client.post(
                f'/api/partidas/{self.match.pk}/resultado/',
                {'home_side': home.pk, 'away_side': away.pk, 'home_score': 0, 'away_score': 0},
                format='json',
            ).status_code,
            200,
        )
        self.url = f'/api/partidas/{self.match.pk}/metricas/'

    def test_records_only_given_fields_and_does_not_duplicate(self):
        first = self.client.post(self.url, {'player': self.player.pk, 'yellow_cards': 1, 'saves': 0}, format='json')
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.data['red_cards'], None)
        second = self.client.post(self.url, {'player': self.player.pk, 'fouls': 2}, format='json')
        self.assertEqual(second.status_code, 200)
        self.assertEqual(MatchMetric.objects.filter(match=self.match, player=self.player).count(), 1)
        self.assertEqual(second.data['yellow_cards'], 1)
        self.assertEqual(second.data['saves'], 0)
        self.assertEqual(second.data['fouls'], 2)

    def test_stats_include_optional_metrics_when_reported(self):
        self.assertEqual(
            self.client.post(
                self.url,
                {'player': self.player.pk, 'yellow_cards': 1, 'red_cards': 0, 'saves': 4},
                format='json',
            ).status_code,
            200,
        )
        response = self.client.get('/api/estatisticas/?kind=pelada')
        row = next(r for r in response.data['ranking'] if r['player'] == self.player.pk)
        self.assertEqual(row['games'], 1)
        self.assertEqual(row['yellow_cards'], 1)
        self.assertEqual(row['red_cards'], 0)
        self.assertEqual(row['saves'], 4)
        self.assertIsNone(row['fouls'])
        reserve = next(r for r in response.data['ranking'] if r['player'] == self.reserve.pk)
        self.assertEqual(reserve['games'], 0)
        general = self.client.get('/api/estatisticas/?kind=geral')
        same = next(r for r in general.data['ranking'] if r['player'] == self.player.pk)
        self.assertEqual(same['saves'], row['saves'])

    def test_member_cannot_edit_and_outsider_cannot_read(self):
        self.client.force_authenticate(self.member)
        self.assertEqual(
            self.client.post(self.url, {'player': self.player.pk, 'saves': 2}, format='json').status_code,
            403,
        )
        self.client.force_authenticate(self.guest)
        self.assertEqual(self.client.get(self.url).status_code, 404)
        self.assertEqual(
            self.client.post(self.url, {'player': self.player.pk, 'saves': 2}, format='json').status_code,
            404,
        )

    def test_requires_lineup_and_value(self):
        not_in_lineup = Player.objects.create(team=self.team, name='Não escalado', shirt_number=3)
        self.assertEqual(self.client.post(self.url, {'player': not_in_lineup.pk, 'saves': 3}).status_code, 400)
        self.assertEqual(self.client.post(self.url, {'player': self.player.pk}).status_code, 400)
