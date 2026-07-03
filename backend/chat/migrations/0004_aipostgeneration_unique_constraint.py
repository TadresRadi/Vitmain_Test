# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_aipostgeneration_posts_review_complete'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='aipostgeneration',
            constraint=models.UniqueConstraint(
                fields=['user'],
                condition=models.Q(posts_review_complete=False),
                name='unique_active_post_generation_per_user'
            ),
        ),
    ]
