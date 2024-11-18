from django.core.management.base import BaseCommand, CommandError
from user_system.models import User
from request_handler.models import Request


class Command(BaseCommand):
    """Build automation command to unseed the database."""

    help = 'Unseeds the database'

    def handle(self, *args, **options):
        User.objects.all().delete()
        Request.objects.all().delete()


