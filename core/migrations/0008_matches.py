"""Cria partidas (modalidade única) e presença Vou/Não vou."""
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('core', '0007_private_teams')]
    operations = [
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120)),
                ('kind', models.CharField(
                    choices=[('pelada', 'Pelada'), ('friendly', 'Amistoso'),
                             ('competition', 'Competição')], default='pelada', max_length=12)),
                ('status', models.CharField(
                    choices=[('scheduled', 'Agendada'), ('canceled', 'Cancelada'),
                             ('in_progress', 'Em andamento'), ('finished', 'Finalizada')],
                    default='scheduled', max_length=12)),
                ('starts_at', models.DateTimeField()),
                ('ends_at', models.DateTimeField()),
                ('location', models.CharField(blank=True, max_length=255)),
                ('expected_players', models.PositiveSmallIntegerField(default=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='matches', to='core.team')),
            ],
            options={'ordering': ['starts_at']},
        ),
        migrations.AddIndex(
            model_name='match',
            index=models.Index(fields=['team', 'starts_at'], name='core_match_team_started_idx'),
        ),
        migrations.CreateModel(
            name='MatchAttendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response', models.CharField(
                    choices=[('going', 'Vou'), ('not_going', 'Não vou')], max_length=10)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='attendances', to='core.match')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='match_attendances', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='matchattendance',
            constraint=models.UniqueConstraint(fields=('match', 'user'), name='unique_match_attendance'),
        ),
    ]
