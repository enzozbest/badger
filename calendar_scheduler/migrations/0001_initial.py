from django.db import migrations
from django.dispatch import receiver 
from django.db.models.signals import post_migrate

# Function to create the default calendar
@receiver(post_migrate)
def create_default_calendar(apps,sender,**kwargs):
    Calendar = apps.get_model('schedule','Calendar')
    Calendar.objects.get_or_create(
        slug="student",
        defaults={"name": "Student Calendar"}
    )
    Calendar.objects.get_or_create(
        slug="tutor",
        defaults={"name": "Tutor Calendar"}
    )

class Migration(migrations.Migration):

    dependencies = [('schedule','0014_use_autofields_for_pk')
    ]

    operations = [
        migrations.RunPython(create_default_calendar),
    ]
