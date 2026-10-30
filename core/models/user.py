"""Usuários: mantém o modelo e histórico de migrações do projeto original."""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O e-mail é obrigatório.')
        user = self.model(email=self.normalize_email(email).lower(), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if not extra_fields['is_staff'] or not extra_fields['is_superuser']:
            raise ValueError('Superusuário precisa ser staff e superuser.')
        return self.create_user(email, password, **extra_fields)


def profile_photo_path(instance, filename):
    # Nome gerado no servidor, para não confiar no nome enviado pelo usuário.
    import uuid
    from pathlib import Path

    return f'profiles/{instance.pk}/{uuid.uuid4().hex}{Path(filename).suffix.lower()}'


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True, verbose_name=_('email'))
    name = models.CharField(max_length=255, blank=True, null=True)
    # Nullable apenas para compatibilidade com contas existentes.
    username = models.CharField(max_length=50, unique=True, null=True, blank=True)
    photo = models.ImageField(upload_to=profile_photo_path, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
