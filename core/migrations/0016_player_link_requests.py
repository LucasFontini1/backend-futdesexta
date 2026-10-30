"""Pedidos de vinculação de jogador autenticado a um elenco."""
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    dependencies = [('core', '0015_locations')]
    operations = [
        migrations.CreateModel(name='PlayerLinkRequest', fields=[
            ('id', models.BigAutoField(primary_key=True, serialize=False)),
            ('status', models.CharField(choices=[
                ('pending', 'Pendente'), ('approved', 'Aprovado'), ('rejected', 'Recusado')
            ], default='pending', max_length=10)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('player', models.ForeignKey(to='core.player', related_name='link_requests', on_delete=django.db.models.deletion.CASCADE)),
            ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='player_link_requests', on_delete=django.db.models.deletion.CASCADE)),
        ]),
        migrations.AddConstraint(
            model_name='playerlinkrequest',
            constraint=models.UniqueConstraint(fields=('player', 'user'), condition=Q(status='pending'), name='unique_pending_player_link'),
        ),
    ]
