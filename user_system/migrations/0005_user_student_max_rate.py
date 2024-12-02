# Generated by Django 4.0.6 on 2024-12-01 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_system', '0004_alter_day_day'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='student_max_rate',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Enter the maximum hourly rate you are willing to pay, in GBP.', max_digits=6, null=True),
        ),
    ]
