"""Regras de peladas e vinculação de ocorrências geradas."""
import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('core', '0009_football')]
    operations = [
        migrations.CreateModel(name='RecurrenceRule', fields=[
            ('id', models.BigAutoField(primary_key=True, serialize=False)),
            ('title', models.CharField(max_length=120)),
            ('weekday', models.PositiveSmallIntegerField(validators=[django.core.validators.MaxValueValidator(6)])),
            ('start_time', models.TimeField()),
            ('end_time', models.TimeField()),
            ('starts_on', models.DateField()),
            ('until', models.DateField(blank=True, null=True)),
            ('location', models.CharField(blank=True, max_length=255)),
            ('expected_players', models.PositiveSmallIntegerField(default=10)),
            ('interval_weeks', models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(8)])),
            ('active', models.BooleanField(default=True)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('team', models.ForeignKey(to='core.team', related_name='recurrences', on_delete=django.db.models.deletion.CASCADE)),
            ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
        ]),
        migrations.CreateModel(name='RecurrenceOccurrence', fields=[
            ('id', models.BigAutoField(primary_key=True, serialize=False)),
            ('starts_at', models.DateTimeField()),
            ('rule', models.ForeignKey(to='core.recurrencerule', related_name='occurrences', on_delete=django.db.models.deletion.CASCADE)),
            ('match', models.OneToOneField(to='core.match', related_name='recurrence_link', on_delete=django.db.models.deletion.CASCADE)),
        ]),
        migrations.AddConstraint(
            model_name='recurrenceoccurrence',
            constraint=models.UniqueConstraint(fields=('rule', 'starts_at'), name='unique_recurrence_occurrence'),
        ),
    ]
