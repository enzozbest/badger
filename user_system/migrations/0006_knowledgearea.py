# Generated by Django 4.0.6 on 2024-11-15 22:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_system', '0005_alter_user_user_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='KnowledgeArea',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=30)),
                ('user', models.ForeignKey(limit_choices_to={'is_tutor': True}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
