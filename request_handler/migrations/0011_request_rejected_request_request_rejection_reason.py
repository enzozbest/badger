

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('request_handler', '0010_request_day2'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='rejected_request',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='request',
            name='rejection_reason',
            field=models.TextField(blank=True, null=True),
        ),
    ]
