"""Serializadores distintos para descoberta pública e perfil privado."""
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from core.models import User


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
        if value is not None and value.size > 3 * 1024 * 1024:
            raise serializers.ValidationError('Imagem limitada a 3 MB.')
        return value


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    password_confirm = serializers.CharField(write_only=True, trim_whitespace=False)
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'username', 'password', 'password_confirm']
        read_only_fields = ['id']
        extra_kwargs = {'name': {'required': True, 'allow_blank': False},
                        'username': {'required': True, 'allow_blank': False}}

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
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({'password_confirm': 'As senhas não coincidem.'})
        try:
            validate_password(attrs['password'])
        except DjangoValidationError as exc:
            raise serializers.ValidationError({'password': list(exc.messages)}) from exc
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
