from django.test import TestCase

from calendar_scheduler.models import Booking
from user_system.fixtures import create_test_users
from user_system.models.user_model import User


class BookingModelTest(TestCase):
    def setUp(self):
        # Create a sample object
        create_test_users.create_test_users()
        self.tutor = User.objects.get(user_type=User.ACCOUNT_TYPE_TUTOR)
        self.student = User.objects.get(user_type=User.ACCOUNT_TYPE_STUDENT)
        self.booking = Booking.objects.create(
            student = self.student,
            tutor = self.tutor,
            knowledge_area = "Python",
            term = "September",
        )

    # Test if a booking object is created successfully.
    def test_book_creation(self):
        self.assertEqual(self.booking.knowledge_area, "Python")
        self.assertEqual(self.booking.term, "September")

    # Test the __str__ method of the Booking model.
    def test_str_representation(self):
        string_booking = f"{self.student} is taught by {self.tutor} in the term {self.booking.term}."
        self.assertEqual(str(self.booking), string_booking)