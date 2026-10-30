"""Valida conflitos de agenda, sem comprometer a privacidade das equipes."""
from datetime import timedelta

from django.db import transaction
from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from core.models import Competition, CompetitionTeam, Match, Team, TeamMembership, User
from core.services.schedule import assert_teams_available


class ScheduleConflictsTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('schedule-owner@example.com', 'secure-password-123')
        self.opponent = User.objects.create_user('schedule-opponent@example.com', 'secure-password-123')
        self.first = Team.objects.create(name='Azul', owner=self.owner)
        self.second = Team.objects.create(name='Verde', owner=self.opponent)
        TeamMembership.objects.create(team=self.first, user=self.owner, role='owner')
        TeamMembership.objects.create(team=self.second, user=self.opponent, role='owner')
        self.starts_at = timezone.now() + timedelta(days=7)
        self.ends_at = self.starts_at + timedelta(hours=2)
        self.client = APIClient()

    def test_rejects_overlap_including_boundary(self):
        Match.objects.create(
            team=self.first, title='Já agendado',
            starts_at=self.starts_at, ends_at=self.ends_at,
        )
        with self.assertRaises(ValidationError), transaction.atomic():
            assert_teams_available(
                [self.first.pk, self.second.pk],
                self.starts_at + timedelta(minutes=15),
                self.ends_at + timedelta(minutes=15),
            )
        with transaction.atomic():
            assert_teams_available(
                [self.first.pk, self.second.pk],
                self.ends_at,
                self.ends_at + timedelta(hours=1),
            )

    def test_canceled_match_does_not_reserve_time(self):
        Match.objects.create(
            team=self.second, title='Cancelado', status=Match.Status.CANCELED,
            starts_at=self.starts_at, ends_at=self.ends_at,
        )
        with transaction.atomic():
            assert_teams_available([self.first.pk, self.second.pk], self.starts_at, self.ends_at)

    def test_invited_friendly_cannot_overlap_another_match(self):
        Match.objects.create(
            team=self.first, title='Pelada já agendada',
            starts_at=self.starts_at, ends_at=self.ends_at,
        )
        self.client.force_authenticate(self.owner)
        invited = self.client.post(
            '/api/amistosos/',
            {
                'from_team': self.first.pk, 'to_team': self.second.pk,
                'starts_at': self.starts_at.isoformat(),
                'ends_at': self.ends_at.isoformat(),
            },
            format='json',
        )
        self.assertEqual(invited.status_code, 201)
        self.client.force_authenticate(self.opponent)
        response = self.client.post(
            f'/api/amistosos/{invited.data["id"]}/responder/',
            {'accept': True},
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Match.objects.filter(kind=Match.Kind.FRIENDLY).count(), 0)

    def test_competition_fixture_rejects_conflicting_team(self):
        Match.objects.create(
            team=self.second, title='Outra partida',
            starts_at=self.starts_at, ends_at=self.ends_at,
        )
        competition = Competition.objects.create(
            owner=self.owner, name='Copa de Sexta', format=Competition.Format.LEAGUE
        )
        CompetitionTeam.objects.create(competition=competition, team=self.first)
        CompetitionTeam.objects.create(competition=competition, team=self.second)
        self.client.force_authenticate(self.owner)
        response = self.client.post(
            f'/api/competicoes/{competition.pk}/jogos/',
            {
                'home_team': self.first.pk,
                'away_team': self.second.pk,
                'starts_at': self.starts_at.isoformat(),
                'ends_at': self.ends_at.isoformat(),
            },
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Match.objects.filter(kind=Match.Kind.COMPETITION).count(), 0)
