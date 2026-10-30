"""Consulta meteorológica real com cache e estados indisponíveis."""
import json
from datetime import timezone as dt_timezone
from urllib.parse import urlencode
from urllib.request import urlopen
from django.core.cache import cache
from django.utils import timezone


def get_forecast(match):
    if match.latitude is None or match.longitude is None:
        return {'state': 'unavailable', 'reason': 'Local sem coordenadas.'}
    delta = match.starts_at - timezone.now()
    if delta.total_seconds() < 0 or delta.days >= 15:
        return {'state': 'unavailable', 'reason': 'Data fora do horizonte da previsão.'}
    key = f'weather:{match.pk}:{int(match.starts_at.timestamp())}'
    cached = cache.get(key)
    if cached:
        return cached
    url = 'https://api.open-meteo.com/v1/forecast?' + urlencode({
        'latitude': match.latitude, 'longitude': match.longitude,
        'hourly': 'temperature_2m,precipitation_probability,weather_code',
        'forecast_days': 16, 'timezone': 'UTC',
    })
    try:
        with urlopen(url, timeout=5) as response:
            data = json.loads(response.read(500000))
        hourly = data['hourly']
        hour = match.starts_at.astimezone(dt_timezone.utc).strftime('%Y-%m-%dT%H:00')
        index = hourly['time'].index(hour)
        result = {
            'state': 'available',
            'temperature_c': hourly['temperature_2m'][index],
            'precipitation_probability_percent': hourly['precipitation_probability'][index],
            'weather_code': hourly['weather_code'][index],
            'consulted_at': timezone.now().isoformat(),
            'source': 'Open-Meteo',
        }
        cache.set(key, result, timeout=3600)
        return result
    except (OSError, ValueError, KeyError, IndexError, TypeError):
        return {'state': 'unavailable', 'reason': 'Previsão indisponível no momento.'}
