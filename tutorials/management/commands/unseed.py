from django.core.management.base import BaseCommand, CommandError
from tutorials.models import User


class Command(BaseCommand):
    """Build automation command to unseed the database."""

    help = 'Unseeds the database'

    def handle(self, *args, **options):
        User.objects.all().delete()


