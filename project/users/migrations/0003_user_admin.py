# Generated by Django 5.1.4 on 2024-12-12 03:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='admin',
            field=models.BooleanField(default=False),
        ),
    ]
