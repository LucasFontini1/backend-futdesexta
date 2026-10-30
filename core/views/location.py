"""Geocodificação sob limite de requisição e previsão por partida autorizada."""

import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.core.cache import cache
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from core.models import Match
from core.services.weather import get_forecast


class GeocodeView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'geocoding'

    def get(self, request):
        text = request.query_params.get('q', '').strip()
        if not 3 <= len(text) <= 120:
            return Response({'detail': 'Informe um endereço de 3 a 120 caracteres.'}, status=400)
        key = 'geocode:' + text.casefold()
        cached = cache.get(key)
        if cached is not None:
            return Response(cached)
        if not cache.add('nominatim-rate-limit', True, timeout=2):
            return Response({'detail': 'Aguarde antes da próxima pesquisa de endereço.'}, status=429)
        url = 'https://nominatim.openstreetmap.org/search?' + urlencode({
            'q': text,
            'format': 'jsonv2',
            'limit': 5,
        })
        req = Request(
            url,
            headers={
                'User-Agent': 'FutdeSexta/0.1 (https://github.com/LucasFontini1/frontend-futdesexta)',
                'Accept': 'application/json',
            },
        )
        try:
            with urlopen(req, timeout=5) as response:
                data = json.loads(response.read(200000))
            places = [
                {'name': item.get('display_name', ''), 'latitude': float(item['lat']), 'longitude': float(item['lon'])}
                for item in data[:5]
            ]
            cache.set(key, places, 86400)
            return Response(places)
        except (OSError, ValueError, KeyError, TypeError):
            return Response({'detail': 'Serviço de endereços indisponível.'}, status=503)


class MatchWeatherView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        matches = Match.objects.filter(
            Q(team__memberships__user=request.user)
            | Q(sides__team__memberships__user=request.user)
            | Q(competition_fixture__competition__owner=request.user)
            | Q(competition_fixture__competition__administrators__user=request.user)
        ).distinct()
        match = get_object_or_404(matches, pk=pk)
        return Response(get_forecast(match))
