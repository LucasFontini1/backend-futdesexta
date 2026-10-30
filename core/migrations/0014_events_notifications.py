"""Eventos, presenças, notificações e inscrições push."""
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    dependencies = [('core', '0013_competition_byes')]
    operations = [
        migrations.CreateModel(name='TeamEvent', fields=[
            ('id', models.BigAutoField(primary_key=True, serialize=False)),
            ('title', models.CharField(max_length=120)),
            ('description', models.TextField(blank=True)),
            ('category', models.CharField(default='other', max_length=40)),
            ('image', models.ImageField(upload_to='events/', blank=True, null=True)),
            ('starts_at', models.DateTimeField()),
            ('ends_at', models.DateTimeField()),
            ('location', models.CharField(max_length=255, blank=True)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('team', models.ForeignKey(to='core.team', related_name='events', on_delete=django.db.models.deletion.CASCADE)),
            ('organizer', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
        ]),
        migrations.CreateModel(name='EventAttendance', fields=[
            ('id', models.BigAutoField(primary_key=True, serialize=False)),
            ('response', models.CharField(choices=[('going', 'Vou'), ('not_going', 'Não vou')], max_length=10)),
            ('event', models.ForeignKey(to='core.teamevent', related_name='attendances', on_delete=django.db.models.deletion.CASCADE)),
            ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.CASCADE)),
        ]),
        migrations.AddConstraint(model_name='eventattendance', constraint=models.UniqueConstraint(fields=('event', 'user'), name='unique_event_attendance')),
        migrations.CreateModel(name='Notification', fields=[
            ('id', models.BigAutoField(primary_key=True, serialize=False)),
            ('kind', models.CharField(max_length=60)),
            ('title', models.CharField(max_length=255)),
            ('link', models.CharField(max_length=255, blank=True)),
            ('dedupe_key', models.CharField(max_length=150, blank=True)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('read_at', models.DateTimeField(null=True, blank=True)),
            ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='notifications', on_delete=django.db.models.deletion.CASCADE)),
        ], options={'ordering': ['-created_at']}),
        migrations.AddConstraint(model_name='notification', constraint=models.UniqueConstraint(fields=('user', 'dedupe_key'), condition=~Q(dedupe_key=''), name='unique_notification_dedupe_key')),
        migrations.CreateModel(name='PushSubscription', fields=[
            ('id', models.BigAutoField(primary_key=True, serialize=False)),
            ('endpoint', models.URLField(max_length=1500, unique=True)),
            ('p256dh', models.CharField(max_length=255)),
            ('auth', models.CharField(max_length=255)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='push_subscriptions', on_delete=django.db.models.deletion.CASCADE)),
        ]),
    ]
