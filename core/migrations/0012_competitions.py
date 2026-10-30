"""Competições, equipes cadastradas, convites e confrontos."""
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.db.models import Q, F


class Migration(migrations.Migration):
    dependencies = [('core', '0011_friendlies')]
    operations = [
        migrations.CreateModel(name='Competition', fields=[
            ('id', models.BigAutoField(primary_key=True, serialize=False)),
            ('name', models.CharField(max_length=120)),
            ('description', models.TextField(blank=True)),
            ('image', models.ImageField(blank=True, null=True, upload_to='competitions/')),
            ('rules', models.TextField(blank=True)),
            ('format', models.CharField(choices=[('league', 'Pontos corridos'), ('knockout', 'Mata-mata')], max_length=12)),
            ('starts_on', models.DateField(blank=True, null=True)),
            ('ends_on', models.DateField(blank=True, null=True)),
            ('is_active', models.BooleanField(default=True)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='competitions_owned', on_delete=django.db.models.deletion.PROTECT)),
        ]),
        migrations.CreateModel(name='CompetitionAdmin', fields=[
            ('id', models.BigAutoField(primary_key=True, serialize=False)),
            ('competition', models.ForeignKey(to='core.competition', related_name='administrators', on_delete=django.db.models.deletion.CASCADE)),
            ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.CASCADE)),
        ]),
        migrations.AddConstraint(model_name='competitionadmin', constraint=models.UniqueConstraint(fields=('competition', 'user'), name='unique_competition_admin')),
        migrations.CreateModel(name='CompetitionInvitation', fields=[
            ('id', models.BigAutoField(primary_key=True, serialize=False)),
            ('status', models.CharField(choices=[('pending', 'Pendente'), ('accepted', 'Aceito'), ('declined', 'Recusado')], default='pending', max_length=10)),
            ('sent_at', models.DateTimeField(auto_now_add=True)),
            ('competition', models.ForeignKey(to='core.competition', related_name='invitations', on_delete=django.db.models.deletion.CASCADE)),
            ('team', models.ForeignKey(to='core.team', related_name='competition_invitations', on_delete=django.db.models.deletion.CASCADE)),
        ]),
        migrations.AddConstraint(model_name='competitioninvitation', constraint=models.UniqueConstraint(fields=('competition', 'team'), name='unique_competition_invitation')),
        migrations.CreateModel(name='CompetitionTeam', fields=[
            ('id', models.BigAutoField(primary_key=True, serialize=False)),
            ('competition', models.ForeignKey(to='core.competition', related_name='participants', on_delete=django.db.models.deletion.CASCADE)),
            ('team', models.ForeignKey(to='core.team', related_name='competition_participations', on_delete=django.db.models.deletion.PROTECT)),
        ]),
        migrations.AddConstraint(model_name='competitionteam', constraint=models.UniqueConstraint(fields=('competition', 'team'), name='unique_competition_participant')),
        migrations.CreateModel(name='CompetitionFixture', fields=[
            ('id', models.BigAutoField(primary_key=True, serialize=False)),
            ('round', models.PositiveSmallIntegerField(default=1)),
            ('competition', models.ForeignKey(to='core.competition', related_name='fixtures', on_delete=django.db.models.deletion.CASCADE)),
            ('match', models.OneToOneField(to='core.match', related_name='competition_fixture', on_delete=django.db.models.deletion.CASCADE)),
            ('home_team', models.ForeignKey(to='core.team', related_name='home_fixtures', on_delete=django.db.models.deletion.PROTECT)),
            ('away_team', models.ForeignKey(to='core.team', related_name='away_fixtures', on_delete=django.db.models.deletion.PROTECT)),
            ('winner', models.ForeignKey(to='core.team', related_name='+', null=True, blank=True, on_delete=django.db.models.deletion.PROTECT)),
        ]),
        migrations.AddConstraint(model_name='competitionfixture', constraint=models.CheckConstraint(condition=~Q(home_team=F('away_team')), name='different_competition_fixture_teams')),
    ]
