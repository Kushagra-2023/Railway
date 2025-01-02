# Generated by Django 5.1.4 on 2024-12-30 03:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0011_remove_booking_destination_station_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='booking_status',
            field=models.CharField(choices=[('CONFIRMED', 'CONFIRMED'), ('WAITLISTED', 'WAITLISTED'), ('CANCELLED', 'CANCELLED')], default='WAITLISTED', max_length=20),
        ),
    ]