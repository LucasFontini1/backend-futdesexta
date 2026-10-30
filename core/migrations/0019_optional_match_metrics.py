"""Estatísticas opcionais independentes do registro oficial de gols."""
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('core', '0018_notification_push_status')]
    operations = [
        migrations.CreateModel(
            name='MatchMetric',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('yellow_cards', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('red_cards', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('fouls', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('saves', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('match', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, related_name='metrics', to='core.match',
                )),
                ('player', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT, related_name='metrics', to='core.player',
                )),
            ],
        ),
        migrations.AddConstraint(
            model_name='matchmetric',
            constraint=models.UniqueConstraint(
                fields=('match', 'player'), name='unique_match_player_metric',
            ),
        ),
    ]
