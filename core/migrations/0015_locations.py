"""Localizações em partidas e eventos."""
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('core', '0014_events_notifications')]
    operations = [
        migrations.AddField(model_name='match', name='latitude',
            field=models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True,
                validators=[django.core.validators.MinValueValidator(-90), django.core.validators.MaxValueValidator(90)])),
        migrations.AddField(model_name='match', name='longitude',
            field=models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True,
                validators=[django.core.validators.MinValueValidator(-180), django.core.validators.MaxValueValidator(180)])),
        migrations.AddField(model_name='teamevent', name='latitude',
            field=models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True,
                validators=[django.core.validators.MinValueValidator(-90), django.core.validators.MaxValueValidator(90)])),
        migrations.AddField(model_name='teamevent', name='longitude',
            field=models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True,
                validators=[django.core.validators.MinValueValidator(-180), django.core.validators.MaxValueValidator(180)])),
    ]
