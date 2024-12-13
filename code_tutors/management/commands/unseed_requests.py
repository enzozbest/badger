from django.core.management import BaseCommand, call_command

from request_handler.models.request_model import Request


class Command(BaseCommand):
    """Build automation command to unseed the database."""

    help = 'Unseeds the database'

    def handle(self, *args, **options):
        Request.objects.all().delete()
        call_command('unseed_bookings')  # There can be no bookings if there are no requests
