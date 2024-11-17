from django.core.management import call_command
from django.core.management.base import BaseCommand



class Command(BaseCommand):
    """Build automation command to seed the database."""
    help = 'Seeds the database by running seed_users and seed_requests commands.'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting the database seeding process...')

        # Run the seed_users command
        self.stdout.write('Seeding users...')
        call_command('seed_users')

        # Run the seed_requests command
        self.stdout.write('Seeding requests...')
        call_command('seed_requests')

        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))







       




