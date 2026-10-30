"""Rankings derivados de resultados, separados por pelada, amistoso e competição."""
from datetime import date
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from core.models import GoalEvent, LineupSlot, Match, MatchResult, Player


def summarize_player(player, results):
    played = goals = conceded = wins = draws = losses = 0
    for result in results:
        slot = LineupSlot.objects.filter(match=result.match, player=player).first()
        if not slot:
            continue
        played += 1
        if slot.side_id == result.home_side_id:
            ours, theirs = result.home_score, result.away_score
        elif slot.side_id == result.away_side_id:
            ours, theirs = result.away_score, result.home_score
        else:
            continue
        if ours > theirs:
            wins += 1
        elif ours < theirs:
            losses += 1
        else:
            draws += 1
        goals += GoalEvent.objects.filter(result=result, scorer=player, own_goal=False).count()
        conceded += GoalEvent.objects.filter(result=result, conceded_by=player).count()
    return {
        'player': player.id, 'name': player.name, 'team': player.team_id,
        'games': played, 'goals': goals, 'goals_conceded_identified': conceded,
        'wins': wins, 'draws': draws, 'losses': losses,
    }


class StatisticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        kind = request.query_params.get('kind', 'geral')
        if kind not in ('geral', Match.Kind.PELADA, Match.Kind.FRIENDLY, Match.Kind.COMPETITION):
            return Response({'detail': 'Modalidade inválida.'}, status=400)
        team_id = request.query_params.get('team')
        if team_id and not team_id.isdigit():
            return Response({'detail': 'Equipe inválida.'}, status=400)
        qs = MatchResult.objects.filter(
            match__team__memberships__user=request.user
        ).select_related('match').distinct()
        players = Player.objects.filter(team__memberships__user=request.user).distinct()
        if team_id:
            qs = qs.filter(match__team_id=int(team_id))
            players = players.filter(team_id=int(team_id))
        if kind != 'geral':
            qs = qs.filter(match__kind=kind)
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        try:
            if start:
                qs = qs.filter(match__starts_at__date__gte=date.fromisoformat(start))
            if end:
                qs = qs.filter(match__starts_at__date__lte=date.fromisoformat(end))
        except ValueError:
            return Response({'detail': 'Período inválido.'}, status=400)
        results = list(qs)
        rows = [summarize_player(player, results) for player in players]
        rows.sort(key=lambda row: (-row['goals'], -row['wins'], row['name']))
        return Response({'kind': kind, 'ranking': rows, 'matches_count': len(results)})
