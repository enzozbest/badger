import datetime

import django.db.models.deletion as deletion
from django.conf import settings
from django.db import migrations, models
from django.db.models.signals import post_migrate
from django.dispatch import receiver


def create_calendars_in_db(Calendar):
    Calendar.objects.get_or_create(
        slug="student",
        defaults={"name": "Student Calendar"}
    )
    Calendar.objects.get_or_create(
        slug="tutor",
        defaults={"name": "Tutor Calendar"}
    )


# Function to create the default calendar
@receiver(post_migrate)
def create_default_calendar(apps=None, sender=None, **kwargs):
    if apps:
        Calendar = apps.get_model('schedule', 'Calendar')
    else:
        from django.apps import apps
        Calendar = apps.get_model('schedule', 'Calendar')
    create_calendars_in_db(Calendar)


class Migration(migrations.Migration):
    initial = True

    dependencies = [('schedule', '0014_use_autofields_for_pk'),
                    migrations.swappable_dependency(settings.AUTH_USER_MODEL),
                    ('user_system', '0001_initial'),
                    ('request_handler', '0001_initial'),
                    ]

    operations = [
        migrations.RunPython(create_default_calendar),

        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('knowledge_area', models.CharField(max_length=255)),
                ('term', models.CharField(max_length=255, null=True)),
                ('frequency', models.CharField(default='Weekly', max_length=255, null=True)),
                ('duration', models.CharField(default='1h', max_length=255)),
                ('is_recurring', models.BooleanField(default=False)),
                ('date', models.DateField(default=datetime.date(1900, 1, 1))),
                ('day', models.ForeignKey(blank=True, null=True, on_delete=deletion.SET_NULL,
                                          related_name='booking_allocated_day', to='user_system.day')),
                ('student', models.ForeignKey(default=None, null=True, on_delete=deletion.CASCADE,
                                              related_name='booking_student', to=settings.AUTH_USER_MODEL)),
                ('tutor',
                 models.ForeignKey(blank=True, default=None, null=True, on_delete=deletion.SET_NULL,
                                   related_name='booking_tutor', to=settings.AUTH_USER_MODEL)),
                ('venue', models.ForeignKey(blank=True, null=True, on_delete=deletion.SET_NULL,
                                            related_name='booking_allocated_venue', to='request_handler.venue')),
            ],
        ),
        migrations.AddField(
            model_name='booking',
            name='cancellation_requested',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='booking',
            name='lesson_identifier',
            field=models.IntegerField(default=-1),
        ),
        migrations.AddField(
            model_name='booking',
            name='title',
            field=models.CharField(default='Tutor session', max_length=255),
        ),
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
        migrations.RemoveField(
            model_name='booking',
            name='end',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='start',
        ),
    ]
