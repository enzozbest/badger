from django.core.management import BaseCommand

from calendar_scheduler.models import Booking


class Command(BaseCommand):
    """Build automation command to unseed the database."""

    help = 'Unseeds the Bookings in database'

    def handle(self, *args, **options):
        Booking.objects.all().delete()
