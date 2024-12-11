from django.db import migrations
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
    dependencies = [('schedule', '0014_use_autofields_for_pk')
                    ]

    operations = [
        migrations.RunPython(create_default_calendar),
    ]
