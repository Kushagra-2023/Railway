# Generated by Django 5.1.4 on 2024-12-18 03:54

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0005_remove_schedule_train'),
        ('users', '0003_user_admin'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='name',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='booking_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='booking',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.user'),
        ),
    ]