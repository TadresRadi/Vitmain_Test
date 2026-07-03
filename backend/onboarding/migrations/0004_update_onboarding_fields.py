# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('onboarding', '0003_alter_onboardingresponse_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='onboardingresponse',
            name='governorate',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='onboardingresponse',
            name='business_subtype',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='onboardingresponse',
            name='marketing_goals',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='onboardingresponse',
            name='target_audience_other',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='onboardingresponse',
            name='tone_of_voice',
            field=models.CharField(max_length=255),
        ),
        migrations.AddField(
            model_name='onboardingresponse',
            name='tone_of_voice_other',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.RemoveField(
            model_name='onboardingresponse',
            name='marketing_goal',
        ),
        migrations.RemoveField(
            model_name='onboardingresponse',
            name='image_style',
        ),
        migrations.RemoveField(
            model_name='onboardingresponse',
            name='mood_style',
        ),
    ]
