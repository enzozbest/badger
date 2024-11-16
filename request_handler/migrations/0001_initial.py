# Generated by Django 4.0.6 on 2024-11-16 00:39

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Day',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Modality',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mode', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('allocated', models.BooleanField(blank=True, default=False)),
                ('knowledge_area', models.CharField(max_length=255)),
                ('term', models.CharField(max_length=255)),
                ('frequency', models.CharField(max_length=255)),
                ('duration', models.CharField(max_length=255)),
                ('availability', models.ManyToManyField(to='request_handler.day')),
            ],
        ),
    ]
