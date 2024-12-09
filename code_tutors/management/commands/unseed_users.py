from django.core.management import BaseCommand, call_command

from user_system.models.user_model import User


class Command(BaseCommand):
    """Build automation command to unseed the database."""

    help = 'Unseeds the database'

    def handle(self, *args, **options):
        User.objects.all().delete()
        call_command('unseed_requests')  # If users are deleted, requests related to those users should also be deleted.
