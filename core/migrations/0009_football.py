"""Gerado para entidades de escalações e resultados oficiais."""
import django.db.models.deletion
import django.core.validators
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('core', '0008_matches')]
    operations = [
        migrations.CreateModel(name='MatchSide', fields=[
            ('id', models.BigAutoField(primary_key=True, serialize=False)),
            ('name', models.CharField(max_length=100)),
            ('color', models.CharField(default='#22c55e', max_length=7)),
            ('order', models.PositiveSmallIntegerField()),
            ('match', models.ForeignKey(to='core.match', on_delete=django.db.models.deletion.CASCADE, related_name='sides')),
            ('team', models.ForeignKey(to='core.team', null=True, blank=True, on_delete=django.db.models.deletion.PROTECT, related_name='match_sides')),
        ], options={'ordering': ['order']}),
        migrations.AddConstraint(model_name='matchside', constraint=models.UniqueConstraint(fields=('match', 'order'), name='unique_match_side_order')),
        migrations.AddConstraint(model_name='matchside', constraint=models.UniqueConstraint(fields=('match', 'name'), name='unique_match_side_name')),
        migrations.CreateModel(name='LineupSlot', fields=[
            ('id', models.BigAutoField(primary_key=True, serialize=False)),
            ('position', models.CharField(blank=True, max_length=40)),
            ('goalkeeper', models.BooleanField(default=False)),
            ('reserve', models.BooleanField(default=False)),
            ('x', models.PositiveSmallIntegerField(default=50, validators=[django.core.validators.MaxValueValidator(100)])),
            ('y', models.PositiveSmallIntegerField(default=50, validators=[django.core.validators.MaxValueValidator(100)])),
            ('match', models.ForeignKey(to='core.match', on_delete=django.db.models.deletion.CASCADE, related_name='lineup_slots')),
            ('side', models.ForeignKey(to='core.matchside', on_delete=django.db.models.deletion.CASCADE, related_name='lineup_slots')),
            ('player', models.ForeignKey(to='core.player', on_delete=django.db.models.deletion.PROTECT, related_name='lineup_slots')),
        ]),
        migrations.AddConstraint(model_name='lineupslot', constraint=models.UniqueConstraint(fields=('match', 'player'), name='unique_player_per_match')),
        migrations.CreateModel(name='MatchResult', fields=[
            ('id', models.BigAutoField(primary_key=True, serialize=False)),
            ('home_score', models.PositiveSmallIntegerField()),
            ('away_score', models.PositiveSmallIntegerField()),
            ('updated_at', models.DateTimeField(auto_now=True)),
            ('match', models.OneToOneField(to='core.match', on_delete=django.db.models.deletion.CASCADE, related_name='result')),
            ('home_side', models.ForeignKey(to='core.matchside', on_delete=django.db.models.deletion.PROTECT, related_name='+')),
            ('away_side', models.ForeignKey(to='core.matchside', on_delete=django.db.models.deletion.PROTECT, related_name='+')),
            ('entered_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
        ]),
        migrations.CreateModel(name='GoalEvent', fields=[
            ('id', models.BigAutoField(primary_key=True, serialize=False)),
            ('own_goal', models.BooleanField(default=False)),
            ('minute', models.PositiveSmallIntegerField(null=True, blank=True)),
            ('result', models.ForeignKey(to='core.matchresult', on_delete=django.db.models.deletion.CASCADE, related_name='goals')),
            ('scoring_side', models.ForeignKey(to='core.matchside', on_delete=django.db.models.deletion.PROTECT)),
            ('scorer', models.ForeignKey(to='core.player', on_delete=django.db.models.deletion.SET_NULL, related_name='goal_events', null=True, blank=True)),
            ('conceded_by', models.ForeignKey(to='core.player', on_delete=django.db.models.deletion.SET_NULL, related_name='goals_conceded', null=True, blank=True)),
        ]),
        migrations.CreateModel(name='ResultRevision', fields=[
            ('id', models.BigAutoField(primary_key=True, serialize=False)),
            ('before', models.JSONField(default=dict)),
            ('after', models.JSONField(default=dict)),
            ('timestamp', models.DateTimeField(auto_now_add=True)),
            ('result', models.ForeignKey(to='core.matchresult', on_delete=django.db.models.deletion.CASCADE, related_name='revisions')),
            ('changed_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
        ]),
    ]
