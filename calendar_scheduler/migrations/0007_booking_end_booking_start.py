# Generated by Django 4.0.6 on 2024-12-11 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calendar_scheduler', '0006_remove_booking_end_remove_booking_start'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='end',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='start',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
