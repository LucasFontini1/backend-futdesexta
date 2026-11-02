from django.test import TestCase
from rest_framework.test import APIClient
from core.models import User

class LoginFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='jogador@example.com', password='SenhaSegura2026!',
            name='Jogador Teste',
        )

    def test_login_and_profile_and_refresh(self):
        response = self.client.post('/api/token/', {
            'email': self.user.email, 'password': 'SenhaSegura2026!',
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        profile = self.client.get('/api/usuarios/me/')
        self.assertEqual(profile.status_code, 200)
        self.assertEqual(profile.data['email'], self.user.email)
        self.assertNotIn('is_superuser', profile.data)
        self.assertNotIn('groups', profile.data)

        refreshed = self.client.post('/api/token/refresh/', {
            'refresh': response.data['refresh'],
        }, format='json')
        self.assertEqual(refreshed.status_code, 200)
        self.assertIn('access', refreshed.data)

    def test_invalid_password_is_denied(self):
        response = self.client.post('/api/token/', {
            'email': self.user.email, 'password': 'errada',
        }, format='json')
        self.assertEqual(response.status_code, 401)

    def test_registration_creates_account_that_can_login(self):
        response = self.client.post('/api/registro/', {
            'email': 'novo@example.com',
            'name': 'Novo Jogador',
            'password': 'SenhaSegura2026!',
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertNotIn('password', response.data)
        registered = User.objects.get(email='novo@example.com')
        self.assertTrue(registered.check_password('SenhaSegura2026!'))
        result = self.client.post('/api/token/', {
            'email': 'novo@example.com',
            'password': 'SenhaSegura2026!',
        }, format='json')
        self.assertEqual(result.status_code, 200)
        self.assertIn('access', result.data)

    def test_registration_rejects_duplicate_email_and_weak_password(self):
        duplicate = self.client.post('/api/registro/', {
            'email': self.user.email,
            'name': 'Duplicado',
            'password': 'SenhaSegura2026!',
        }, format='json')
        self.assertEqual(duplicate.status_code, 400)
        weak = self.client.post('/api/registro/', {
            'email': 'fraco@example.com',
            'name': 'Teste',
            'password': '12345678',
        }, format='json')
        self.assertEqual(weak.status_code, 400)
        self.assertFalse(User.objects.filter(email='fraco@example.com').exists())

    def test_profile_requires_authentication(self):
        self.assertEqual(self.client.get('/api/usuarios/me/').status_code, 401)

    def test_user_listing_does_not_expose_other_accounts(self):
        User.objects.create_user('outra@example.com', 'SenhaSegura2026!')
        self.client.force_authenticate(self.user)
        response = self.client.get('/api/usuarios/')
        self.assertEqual(response.status_code, 200)
        rows = response.data.get('results', response.data)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['email'], self.user.email)
