# Generated by Django 4.0.6 on 2024-11-18 21:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_system', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Day',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.CharField(max_length=10)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='availability',
            field=models.ManyToManyField(default=None, to='user_system.day'),
        ),
    ]
