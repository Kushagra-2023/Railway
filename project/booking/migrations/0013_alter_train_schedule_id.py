# Generated by Django 5.1.4 on 2024-12-30 04:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0012_alter_booking_booking_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='train',
            name='schedule_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trains', to='booking.schedule'),
        ),
    ]
