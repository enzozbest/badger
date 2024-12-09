from django.test import TestCase
from user_system.models.user_model import User
from request_handler.models import Venue
from calendar_scheduler.models import Booking
from datetime import date

class BookingModelTest(TestCase):
    def setUp(self):
        # Create necessary objects for the Booking model
        self.student = User.objects.create(username="@student", email="student@example.com")
        self.tutor = User.objects.create(username="@tutor", email="tutor@example.com")
        self.venue = Venue.objects.create(venue="Online")
        self.term = "September"
        self.booking_date = date(2035, 12, 19)

    def test_booking_str_method(self):
        booking = Booking.objects.create(  # September term booking
            student=self.student,
            tutor=self.tutor,
            term = self.term,
            start="2035-12-19 10:00:00",
            end="2035-12-19 11:00:00",
            lesson_identifier="1",
            date=date(2024, 12, 3)
        )
        expected_str = f"{self.student} is taught by {self.tutor} in the term {self.term}."
        self.assertEqual(str(booking), expected_str)