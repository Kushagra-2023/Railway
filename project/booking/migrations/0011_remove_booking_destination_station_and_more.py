# Generated by Django 5.1.4 on 2024-12-27 04:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0010_booking_destination_station_booking_source_station_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='destination_station',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='source_station',
        ),
        migrations.RemoveField(
            model_name='routestop',
            name='order',
        ),
    ]
