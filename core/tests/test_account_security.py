"""Conta inativa até verificação e recuperação de senha sem enumeração."""
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import TestCase
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APIClient
from core.models import User


class AccountSecurityTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_accept_terms_and_verify_email_before_login(self):
        data = {
            'email': 'verified@example.com', 'username': 'verified_user',
            'name': 'Pessoa Verificada', 'password': 'Strong-Pass-2026!',
            'password_confirm': 'Strong-Pass-2026!', 'accepted_terms': True,
        }
        denied = self.client.post('/api/registro/', {**data, 'accepted_terms': False}, format='json')
        self.assertEqual(denied.status_code, 400)
        response = self.client.post('/api/registro/', data, format='json')
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(email='verified@example.com')
        self.assertFalse(user.is_active)
        self.assertGreater(len(mail.outbox), 0)
        self.assertNotIn('password', response.data)
        unauthorized = self.client.post('/api/token/', {'email': user.email, 'password': data['password']})
        self.assertEqual(unauthorized.status_code, 401)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        result = self.client.post('/api/conta/verificar-email/', {'uid': uid, 'token': token})
        self.assertEqual(result.status_code, 200)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_password_reset_token_single_use(self):
        user = User.objects.create_user(
            'recovery@example.com', 'previous-Pass-2026!', username='recoverer'
        )
        missing = self.client.post('/api/conta/recuperar-senha/', {'email': 'absent@example.com'})
        found = self.client.post('/api/conta/recuperar-senha/', {'email': user.email})
        self.assertEqual(missing.status_code, 200)
        self.assertEqual(found.status_code, 200)
        self.assertEqual(missing.data, found.data)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset = self.client.post('/api/conta/redefinir-senha/', {
            'uid': uid, 'token': token, 'password': 'New-Secure-Pass-2026!',
            'password_confirm': 'New-Secure-Pass-2026!',
        })
        self.assertEqual(reset.status_code, 200)
        user.refresh_from_db()
        self.assertTrue(user.check_password('New-Secure-Pass-2026!'))
        replay = self.client.post('/api/conta/redefinir-senha/', {
            'uid': uid, 'token': token, 'password': 'anotherSecurePass999',
            'password_confirm': 'anotherSecurePass999',
        })
        self.assertEqual(replay.status_code, 400)
