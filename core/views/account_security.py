"""Verificação de e-mail e recuperação de senha com tokens temporários."""
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from core.models import User


def get_user_by_token(uid, token):
    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, UnicodeDecodeError, User.DoesNotExist):
        return None
    return user if default_token_generator.check_token(user, token) else None


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'email_verification'

    def post(self, request):
        user = get_user_by_token(request.data.get('uid', ''), request.data.get('token', ''))
        if not user:
            return Response({'detail': 'Token inválido ou expirado.'}, status=400)
        user.is_active = True
        user.save(update_fields=['is_active'])
        return Response({'verified': True})


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'account_recovery'

    def post(self, request):
        email = str(request.data.get('email', '')).strip().lower()
        if email:
            user = User.objects.filter(email__iexact=email, is_active=True).first()
            if user:
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                url = f"{settings.FRONTEND_URLS[0].rstrip('/')}/redefinir-senha?uid={uid}&token={token}"
                send_mail(
                    'Redefinir senha — Fut de Sexta',
                    f'Se você solicitou a recuperação, acesse: {url}',
                    settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False,
                )
        # Mesma resposta para e-mail inexistente: evita enumeração de contas.
        return Response({'detail': 'Se existir uma conta com este e-mail, enviaremos instruções.'})


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'account_recovery'

    def post(self, request):
        user = get_user_by_token(request.data.get('uid', ''), request.data.get('token', ''))
        if not user or not user.is_active:
            return Response({'detail': 'Token inválido ou expirado.'}, status=400)
        password = request.data.get('password')
        confirm = request.data.get('password_confirm')
        if not isinstance(password, str) or password != confirm:
            return Response({'password_confirm': 'As senhas não coincidem.'}, status=400)
        try:
            validate_password(password, user=user)
        except DjangoValidationError as exc:
            return Response({'password': exc.messages}, status=400)
        user.set_password(password)
        user.save(update_fields=['password'])
        return Response({'changed': True})


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if not user.check_password(str(request.data.get('old_password', ''))):
            return Response({'old_password': 'Senha atual incorreta.'}, status=400)
        new_password = request.data.get('new_password')
        if not isinstance(new_password, str):
            return Response({'new_password': 'Informe uma senha.'}, status=400)
        try:
            validate_password(new_password, user=user)
        except DjangoValidationError as exc:
            return Response({'new_password': exc.messages}, status=400)
        user.set_password(new_password)
        user.save(update_fields=['password'])
        return Response({'changed': True})
