"""Serializers do usuário: dados públicos e cadastro, conforme padrão do tutorial DRF."""
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from core.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email']
        read_only_fields = fields


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)

    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'password']
        read_only_fields = ['id']

    def validate_email(self, value):
        email = User.objects.normalize_email(value.strip())
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError('Já existe uma conta com este e-mail.')
        return email

    def validate_password(self, value):
        candidate = User(email=self.initial_data.get('email', ''), name=self.initial_data.get('name', ''))
        try:
            validate_password(value, user=candidate)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages) from exc
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
