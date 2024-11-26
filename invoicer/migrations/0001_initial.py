# Generated by Django 4.0.6 on 2024-11-23 13:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('invoice_id', models.CharField(max_length=100, primary_key=True, serialize=False, unique=True)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_invoiced', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
