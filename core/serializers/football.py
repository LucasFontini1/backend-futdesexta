"""Validadores de escalações e resultados. Estatísticas vêm das fontes oficiais."""

from rest_framework import serializers

from core.models import GoalEvent, LineupSlot, MatchResult, MatchSide


class MatchSideSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchSide
        fields = ['id', 'match', 'team', 'name', 'color', 'order']
        read_only_fields = ['id', 'match']


class LineupSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = LineupSlot
        fields = ['side', 'player', 'position', 'goalkeeper', 'reserve', 'x', 'y']


class GoalEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoalEvent
        fields = ['scoring_side', 'scorer', 'conceded_by', 'own_goal', 'minute']


class MatchResultSerializer(serializers.ModelSerializer):
    goals = GoalEventSerializer(many=True, required=False)

    class Meta:
        model = MatchResult
        fields = ['id', 'home_side', 'away_side', 'home_score', 'away_score', 'goals', 'updated_at']
        read_only_fields = ['id', 'updated_at']

    def validate(self, data):
        match = self.context['match']
        home, away = data['home_side'], data['away_side']
        if home == away or home.match_id != match.pk or away.match_id != match.pk:
            raise serializers.ValidationError('Os dois lados devem pertencer à partida e ser distintos.')
        if match.sides.count() != 2:
            raise serializers.ValidationError('É obrigatório registrar exatamente dois lados.')
        if set(match.sides.values_list('id', flat=True)) != {home.pk, away.pk}:
            raise serializers.ValidationError('Lados da partida inconsistentes.')
        goals = data.get('goals', [])
        home_count = away_count = 0
        for goal in goals:
            scoring_side = goal['scoring_side']
            if scoring_side.pk not in {home.pk, away.pk}:
                raise serializers.ValidationError('Gol de lado estranho à partida.')
            if scoring_side.pk == home.pk:
                home_count += 1
            else:
                away_count += 1
            scorer = goal.get('scorer')
            keeper = goal.get('conceded_by')
            if scorer:
                scorer_slot = LineupSlot.objects.filter(match=match, player=scorer).first()
                if not scorer_slot:
                    raise serializers.ValidationError('Autor de gol não escalado.')
                same_side = scorer_slot.side_id == scoring_side.pk
                if same_side == bool(goal.get('own_goal', False)):
                    raise serializers.ValidationError(
                        'Gol normal deve ser do autor pelo lado que marcou; gol contra deve beneficiar o adversário.'
                    )
            if keeper:
                eligible = (
                    LineupSlot.objects
                    .filter(match=match, player=keeper, goalkeeper=True)
                    .exclude(side=scoring_side)
                    .exists()
                )
                if not eligible:
                    raise serializers.ValidationError('Goleiro deve estar no lado adversário.')
        if home_count > data['home_score'] or away_count > data['away_score']:
            raise serializers.ValidationError('Gols individuais não podem exceder o placar.')
        return data
