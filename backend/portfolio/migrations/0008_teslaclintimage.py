from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0007_brand'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeslaClientImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, default='', max_length=255)),
                ('image', models.ImageField(upload_to='tesla-client/')),
                ('order', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Tesla Client Image',
                'verbose_name_plural': 'Tesla Client Images',
                'ordering': ['order', '-created_at'],
            },
        ),
    ]
