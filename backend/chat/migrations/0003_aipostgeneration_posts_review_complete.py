from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='aipostgeneration',
            name='posts_review_complete',
            field=models.BooleanField(default=False),
        ),
    ]
