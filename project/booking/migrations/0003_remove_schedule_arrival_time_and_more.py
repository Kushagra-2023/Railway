# Generated by Django 5.1.4 on 2024-12-15 16:04

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0002_remove_schedule_train'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='schedule',
            name='arrival_time',
        ),
        migrations.RemoveField(
            model_name='schedule',
            name='departure_time',
        ),
        migrations.AddField(
            model_name='route',
            name='via_stations',
            field=models.ManyToManyField(blank=True, related_name='via_routes', to='booking.station'),
        ),
        migrations.AddField(
            model_name='schedule',
            name='arrival',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='schedule',
            name='departure',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='schedule',
            name='train',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to='booking.train'),
        ),
        migrations.AddField(
            model_name='seat',
            name='schedule',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='booking.schedule'),
        ),
        migrations.CreateModel(
            name='RouteStop',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('arrival_time', models.TimeField()),
                ('route', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='route_stops', to='booking.route')),
                ('station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='route_stops', to='booking.station')),
            ],
        ),
    ]