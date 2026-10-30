from django.db import migrations, models
import core.models.user


class Migration(migrations.Migration):
    dependencies = [('core', '0005_remove_user_passage_id')]

    operations = [
        migrations.AddField(
            model_name='user',
            name='username',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='user',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to=core.models.user.profile_photo_path),
        ),
    ]
