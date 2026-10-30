"""Serializadores distintos para descoberta pública e perfil privado."""

from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import serializers

from core.models import User
from core.validators import validate_user_image


class UserSerializer(serializers.ModelSerializer):
    """Somente dados públicos. Nunca expor e-mail/permissões na pesquisa."""

    class Meta:
        model = User
        fields = ['id', 'name', 'username', 'photo']
        read_only_fields = fields


class UserPrivateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'username', 'photo']
        read_only_fields = ['id', 'email']

    def validate_photo(self, value):
        return validate_user_image(value)


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    password_confirm = serializers.CharField(write_only=True, trim_whitespace=False)
    accepted_terms = serializers.BooleanField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'username', 'password', 'password_confirm', 'accepted_terms']
        read_only_fields = ['id']
        extra_kwargs = {
            'name': {'required': True, 'allow_blank': False},
            'username': {'required': True, 'allow_blank': False},
        }

    def validate_username(self, value):
        value = value.strip()
        if not value or not value.replace('_', '').isalnum():
            raise serializers.ValidationError('Use letras, números ou sublinhado.')
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError('Username indisponível.')
        return value

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('E-mail já cadastrado.')
        return value

    def validate(self, attrs):
        if attrs.get('accepted_terms') is not True:
            raise serializers.ValidationError({'accepted_terms': 'É necessário aceitar os termos.'})
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({'password_confirm': 'As senhas não coincidem.'})
        try:
            validate_password(attrs['password'])
        except DjangoValidationError as exc:
            raise serializers.ValidationError({'password': list(exc.messages)}) from exc
        return attrs

    def create(self, validated_data):
        validated_data.pop('accepted_terms', None)
        user = User.objects.create_user(**validated_data, is_active=False)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        frontend = settings.FRONTEND_URLS[0].rstrip('/')
        verification_url = f'{frontend}/verificar-email?uid={uid}&token={token}'
        send_mail(
            subject='Confirme seu cadastro no Fut de Sexta',
            message=f'Para ativar sua conta, acesse: {verification_url}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return user
