# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_customuser_auth_provider_customuser_profile_picture_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='posts_generated',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='customuser',
            name='images_generated',
            field=models.BooleanField(default=False),
        ),
    ]
