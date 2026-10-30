"""Proteção de agenda para impedir jogos simultâneos da mesma equipe.

Usar dentro de transaction.atomic: o bloqueio de linhas de Team torna a
verificação serializada em PostgreSQL, incluindo equipes adversárias.
"""

from django.db.models import Q
from rest_framework.exceptions import ValidationError

from core.models import Match, Team


def assert_teams_available(team_ids, starts_at, ends_at, *, excluded_match=None):
    """Bloqueia equipes, verifica intervalo [início, fim) e conflito privado."""
    ids = sorted(set(int(pk) for pk in team_ids))
    if not ids or ends_at <= starts_at:
        raise ValidationError('Informe equipes e horários válidos.')
    # Select-for-update: transação e ordenação determinística no PostgreSQL.
    locked_ids = list(Team.objects.select_for_update().filter(pk__in=ids).order_by('pk').values_list('pk', flat=True))
    if locked_ids != ids:
        raise ValidationError('Uma das equipes não existe.')
    overlapping = Match.objects.filter(
        Q(team_id__in=ids) | Q(sides__team_id__in=ids),
        status__in=[Match.Status.SCHEDULED, Match.Status.IN_PROGRESS],
        starts_at__lt=ends_at,
        ends_at__gt=starts_at,
    ).distinct()
    if excluded_match:
        overlapping = overlapping.exclude(pk=excluded_match)
    if overlapping.exists():
        raise ValidationError('Há uma partida conflitante na agenda de uma das equipes.')
