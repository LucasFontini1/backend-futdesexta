"""Convites para amistosos entre equipes, com aprovação bilateral."""
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.db.models import Q, F


class Migration(migrations.Migration):
    dependencies = [('core', '0010_recurrence')]
    operations = [
        migrations.CreateModel(name='FriendlyInvitation', fields=[
            ('id', models.BigAutoField(primary_key=True, serialize=False)),
            ('starts_at', models.DateTimeField()),
            ('ends_at', models.DateTimeField()),
            ('location', models.CharField(blank=True, max_length=255)),
            ('message', models.TextField(blank=True)),
            ('status', models.CharField(choices=[
                ('pending', 'Pendente'), ('accepted', 'Aceito'),
                ('declined', 'Recusado'), ('canceled', 'Cancelado')
            ], default='pending', max_length=10)),
            ('result_approved_from', models.BooleanField(default=False)),
            ('result_approved_to', models.BooleanField(default=False)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('from_team', models.ForeignKey(to='core.team', related_name='sent_friendlies', on_delete=django.db.models.deletion.CASCADE)),
            ('to_team', models.ForeignKey(to='core.team', related_name='received_friendlies', on_delete=django.db.models.deletion.CASCADE)),
            ('match', models.OneToOneField(to='core.match', related_name='friendly_invitation', null=True, blank=True, on_delete=django.db.models.deletion.SET_NULL)),
            ('invited_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
        ]),
        migrations.AddConstraint(
            model_name='friendlyinvitation',
            constraint=models.CheckConstraint(condition=~Q(from_team=F('to_team')), name='friendlies_distinct_teams'),
        ),
    ]
