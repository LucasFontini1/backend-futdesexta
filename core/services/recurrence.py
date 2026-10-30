"""Geração atômica de peladas semanais sem duplicar ocorrências."""
from datetime import datetime, timedelta, time
from django.db import transaction
from django.utils import timezone
from core.models import Match, RecurrenceOccurrence


def generate_occurrences(rule, weeks=8):
    if not rule.active:
        return 0
    weeks = min(max(int(weeks), 1), 16)
    today = timezone.localdate()
    start_date = max(today, rule.starts_on)
    first = start_date + timedelta(days=(rule.weekday - start_date.weekday()) % 7)
    tz = timezone.get_current_timezone()
    created = 0
    end_date = start_date + timedelta(weeks=weeks)
    day = first
    while day <= end_date and (rule.until is None or day <= rule.until):
        delta_weeks = (day - rule.starts_on).days // 7
        if delta_weeks >= 0 and delta_weeks % rule.interval_weeks == 0:
            start_time = time.fromisoformat(rule.start_time) if isinstance(rule.start_time, str) else rule.start_time
            end_time = time.fromisoformat(rule.end_time) if isinstance(rule.end_time, str) else rule.end_time
            begin = timezone.make_aware(datetime.combine(day, start_time), tz)
            finish = timezone.make_aware(datetime.combine(day, end_time), tz)
            with transaction.atomic():
                if not RecurrenceOccurrence.objects.filter(rule=rule, starts_at=begin).exists():
                    match = Match.objects.create(
                        team=rule.team, title=rule.title, starts_at=begin, ends_at=finish,
                        location=rule.location, expected_players=rule.expected_players,
                    )
                    try:
                        RecurrenceOccurrence.objects.create(rule=rule, match=match, starts_at=begin)
                        created += 1
                    except Exception:
                        # Falha deve reverter a criação da partida.
                        raise
        day += timedelta(days=7)
    return created
