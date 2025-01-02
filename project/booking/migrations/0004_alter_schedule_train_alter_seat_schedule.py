# Generated by Django 5.1.4 on 2024-12-15 16:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0003_remove_schedule_arrival_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedule',
            name='train',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to='booking.train'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='seat',
            name='schedule',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='booking.schedule'),
            preserve_default=False,
        ),
    ]
