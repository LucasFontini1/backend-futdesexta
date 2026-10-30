"""Contrato de JWT persistente no frontend, inspirado no padrão do projeto Momentum."""

from django.test import TestCase
from rest_framework.test import APIClient

from core.models import User


class JwtSessionContractTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            'jwt-contract@example.com',
            'SecurePassword-2026!',
            username='jwt_contract',
            name='Jogador Teste',
        )

    def test_access_refresh_and_authenticated_profile(self):
        response = self.client.post(
            '/api/token/',
            {'email': self.user.email, 'password': 'SecurePassword-2026!'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')
        profile = self.client.get('/api/usuarios/me/')
        self.assertEqual(profile.status_code, 200)
        self.assertEqual(profile.data['email'], self.user.email)
        renewed = self.client.post(
            '/api/token/refresh/',
            {'refresh': response.data['refresh']},
            format='json',
        )
        self.assertEqual(renewed.status_code, 200)
        self.assertIn('access', renewed.data)

    def test_inactive_user_cannot_get_token(self):
        self.user.is_active = False
        self.user.save(update_fields=['is_active'])
        result = self.client.post(
            '/api/token/',
            {'email': self.user.email, 'password': 'SecurePassword-2026!'},
            format='json',
        )
        self.assertEqual(result.status_code, 401)
