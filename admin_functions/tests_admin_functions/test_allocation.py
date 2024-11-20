from django.test import TestCase

from request_handler.fixtures.create_test_requests import create_test_requests
from request_handler.models import Request
from user_system.fixtures.create_test_users import create_test_user
from user_system.models import User


class TestAllocation(TestCase):
    def setUp(self):
        create_test_user()
        create_test_requests()
        self.admin = User.objects.get(user_type=User.ACCOUNT_TYPE_ADMIN)
        self.tutor = User.objects.get(user_type=User.ACCOUNT_TYPE_TUTOR)
        self.student = User.objects.get(user_type=User.ACCOUNT_TYPE_STUDENT)
        self.allocated_request = Request.objects.get(allocated=True)
        self.unallocated_request = Request.objects.get(allocated=False)


    def test_allocated_request_exists(self):
        self.assertIsNotNone(self.allocated_request)
