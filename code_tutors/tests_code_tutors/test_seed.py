from django.test import TransactionTestCase

from code_tutors.management.commands import seed_requests
from request_handler.models import Request
from user_system.models import User, Day
from django.core.management import call_command
from django.db import transaction
import code_tutors.management.commands.seed_users as seed_users

class TestSeedUsers(TransactionTestCase):
    def setUp(self):
        super().setUp()
        if not Day.objects.exists():
            Day.objects.bulk_create([
                Day(day="Monday"),
                Day(day="Tuesday"),
                Day(day="Wednesday"),
                Day(day="Thursday"),
                Day(day="Friday"),
            ])
        self.before = User.objects.count()
        call_command('seed_users')
        self.after = User.objects.count()

    def tearDown(self):
        User.objects.all().delete()
        Request.objects.all().delete()

    def test_seeding_users(self):
        self.assertEqual(self.before, 0)
        self.assertEqual(self.after, seed_users.Command.USER_COUNT)

    def test_seeding_requests(self):
        before = Request.objects.count()
        call_command('seed_requests')
        after = Request.objects.count()
        self.assertEqual(before, 0)
        self.assertEqual(after, seed_requests.Command.REQUEST_COUNT)
        User.objects.all().delete()


