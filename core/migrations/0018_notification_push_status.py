from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('core', '0017_align_models')]
    operations = [
        migrations.AddField(
            model_name='notification', name='push_sent_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
