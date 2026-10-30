"""Geração de confrontos mata-mata: avanço de vencedores e folgas."""

from django.db import transaction
from rest_framework.exceptions import ValidationError

from core.models import CompetitionBye, CompetitionFixture, Match, MatchSide


def create_knockout_round(competition, teams, round_number, starts_at, ends_at):
    if len(teams) < 2:
        return {'champion': teams[0].pk if teams else None, 'created': 0}
    if ends_at <= starts_at:
        raise ValidationError('A partida precisa terminar depois de começar.')
    if CompetitionFixture.objects.filter(competition=competition, round=round_number).exists():
        raise ValidationError('Essa rodada já foi criada.')
    count = 0
    with transaction.atomic():
        for index in range(0, len(teams) - 1, 2):
            home, away = teams[index : index + 2]
            match = Match.objects.create(
                team=home,
                kind=Match.Kind.COMPETITION,
                title=competition.name,
                starts_at=starts_at,
                ends_at=ends_at,
            )
            MatchSide.objects.create(match=match, team=home, name=home.name, order=1)
            MatchSide.objects.create(match=match, team=away, name=away.name, order=2)
            CompetitionFixture.objects.create(
                competition=competition,
                match=match,
                home_team=home,
                away_team=away,
                round=round_number,
            )
            count += 1
        if len(teams) % 2 == 1:
            CompetitionBye.objects.get_or_create(competition=competition, team=teams[-1], round=round_number)
    return {'created': count, 'round': round_number}
