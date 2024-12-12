from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

from code_tutors.aws.resources.yaml_loader import get_bucket_name
from code_tutors.aws.s3 import _delete, _get_credentials


class Command(BaseCommand):
    """Build automation command to seed the database."""
    help = 'Seeds the database by running seed_users and seed_requests commands.'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting the database seeding process...')

        # Run the seed_users command
        self.stdout.write('Unseeding users...')
        call_command('unseed_users')

        # Run the seed_requests command
        self.stdout.write('Unseeding requests...')
        call_command('unseed_requests')

        self.stdout.write(self.style.SUCCESS('Database unseeding completed successfully!'))

        try:
            if settings.USE_AWS_S3:
                self.stdout.write('Deleting all invoices from S3...')
                credentials = _get_credentials()
                _delete('invoices/pdfs', get_bucket_name('invoicer'), credentials=credentials)
                self.stdout.write(self.style.SUCCESS('Invoices successfully deleted from S3!'))
        except Exception:
            self.stdout.write(self.style.ERROR('Invoices could not be deleted from S3!'))
