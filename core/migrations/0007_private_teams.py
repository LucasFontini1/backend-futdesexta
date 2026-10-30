"""Equipes privadas, convites e jogadores vinculados à equipe."""
import core.models.team
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    dependencies = [('core', '0006_user_profile')]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('description', models.TextField(blank=True)),
                ('color', models.CharField(default='#22c55e', max_length=7)),
                ('emblem', models.ImageField(blank=True, null=True, upload_to='teams/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('owner', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='owned_teams', to=settings.AUTH_USER_MODEL,
                )),
            ],
        ),
        migrations.CreateModel(
            name='TeamMembership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(
                    choices=[('owner', 'Dono'), ('admin', 'Administrador'), ('member', 'Membro')],
                    default='member', max_length=10,
                )),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='memberships', to='core.team')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='team_memberships', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='teammembership',
            constraint=models.UniqueConstraint(fields=('team', 'user'), name='unique_team_user'),
        ),
        migrations.CreateModel(
            name='TeamInvitation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[
                    ('pending', 'Pendente'), ('accepted', 'Aceito'), ('declined', 'Recusado'),
                    ('canceled', 'Cancelado'), ('expired', 'Expirado'),
                ], default='pending', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField(default=core.models.team.invitation_expiry)),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='invitations', to='core.team')),
                ('invitee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='team_invitations', to=settings.AUTH_USER_MODEL)),
                ('invited_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='sent_team_invitations', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='teaminvitation',
            constraint=models.UniqueConstraint(
                condition=Q(status='pending'), fields=('team', 'invitee'),
                name='unique_pending_team_invitation',
            ),
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('shirt_number', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('position', models.CharField(blank=True, max_length=40)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='players/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='players', to='core.team')),
                ('linked_user', models.ForeignKey(blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='player_profiles', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='player',
            constraint=models.UniqueConstraint(
                condition=Q(shirt_number__isnull=False),
                fields=('team', 'shirt_number'), name='unique_player_shirt_per_team',
            ),
        ),
        migrations.AddConstraint(
            model_name='player',
            constraint=models.UniqueConstraint(
                condition=Q(linked_user__isnull=False),
                fields=('team', 'linked_user'), name='unique_player_link_per_team',
            ),
        ),
    ]
