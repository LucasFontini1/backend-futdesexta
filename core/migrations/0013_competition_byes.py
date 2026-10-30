"""Armazena equipes classificadas automaticamente por folga."""
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('core', '0012_competitions')]
    operations = [
        migrations.CreateModel(name='CompetitionBye', fields=[
            ('id', models.BigAutoField(primary_key=True, serialize=False)),
            ('round', models.PositiveSmallIntegerField()),
            ('competition', models.ForeignKey(to='core.competition', related_name='byes', on_delete=django.db.models.deletion.CASCADE)),
            ('team', models.ForeignKey(to='core.team', on_delete=django.db.models.deletion.CASCADE)),
        ]),
        migrations.AddConstraint(
            model_name='competitionbye',
            constraint=models.UniqueConstraint(fields=('competition', 'round', 'team'), name='unique_knockout_bye'),
        ),
    ]
