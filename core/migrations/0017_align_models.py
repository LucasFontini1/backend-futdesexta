"""Sincroniza metadados de campos e índice com os modelos Django atuais."""
from django.db import migrations, models


MODEL_NAMES = [
    'competition', 'competitionadmin', 'competitionbye',
    'competitionfixture', 'competitioninvitation', 'competitionteam',
    'eventattendance', 'friendlyinvitation', 'goalevent', 'lineupslot',
    'matchresult', 'matchside', 'notification', 'playerlinkrequest',
    'pushsubscription', 'recurrenceoccurrence', 'recurrencerule',
    'resultrevision', 'teamevent',
]


class Migration(migrations.Migration):
    dependencies = [('core', '0016_player_link_requests')]
    operations = [
        migrations.RenameIndex(
            model_name='match',
            old_name='core_match_team_started_idx',
            new_name='core_match_team_id_9ad941_idx',
        ),
        *[
            migrations.AlterField(
                model_name=name, name='id',
                field=models.BigAutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID',
                ),
            )
            for name in MODEL_NAMES
        ],
        migrations.AlterField(
            model_name='user', name='email',
            field=models.EmailField(max_length=255, unique=True, verbose_name='email'),
        ),
        migrations.AlterField(
            model_name='user', name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='user', name='is_staff',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='user', name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
