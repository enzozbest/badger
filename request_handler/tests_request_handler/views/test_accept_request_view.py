from datetime import datetime
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from calendar_scheduler.models import Booking
from request_handler.models.request_model import Request
from request_handler.models.venue_model import Venue
from request_handler.views.accept_request import match_lesson_frequency
from user_system.fixtures.create_test_users import create_test_users
from user_system.models.day_model import Day
from user_system.models.user_model import User


class AcceptRequestViewTestCase(TestCase):
    def setUp(self):
        create_test_users()
        self.tutor = User.objects.get(user_type=User.ACCOUNT_TYPE_TUTOR)
        self.student = User.objects.get(user_type=User.ACCOUNT_TYPE_STUDENT)
        self.day_monday, created = Day.objects.get_or_create(day="Monday")
        self.day_friday, created = Day.objects.get_or_create(day="Friday")
        self.venue_online, created = Venue.objects.get_or_create(venue="Online")

        self.lesson_request = Request.objects.create(
            id=1,
            allocated=True,
            tutor=self.tutor,
            student=self.student,
            term="September",
            day=self.day_monday,
            frequency="Weekly",
            duration=60,
            is_recurring=False,
            knowledge_area="Robotics",
            venue=self.venue_online,
        )
        self.client.force_login(self.tutor)
    
    # Test that a booking is successfully created and the associated request is deleted.
    def test_successful_request_handling(self):
        response = self.client.post(reverse('accept_request', args=[self.lesson_request.id]))
        bookings = Booking.objects.filter(tutor=self.tutor)
        self.assertEqual(len(bookings), 15)  # Weekly = 15 sessions
        with self.assertRaises(Request.DoesNotExist):
            Request.objects.get(id=self.lesson_request.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('view_requests'))

    # Test the lesson frequency for weekly bookings.
    @patch('request_handler.views.accept_request.datetime')
    def test_weekly_booking_frequency(self, mock_datetime):
        self.lesson_request.frequency = 'Weekly'
        self.lesson_request.save()
        mock_datetime.today.return_value = datetime(2024, 8, 1)
        # Ensure other datetime methods work normally
        mock_datetime.combine.side_effect = lambda d, t: datetime.combine(d, t)
        response = self.client.post(reverse('accept_request', kwargs={'request_id': self.lesson_request.id}))

        # Check the number of sessions created
        bookings = Booking.objects.all()
        self.assertEqual(bookings.count(), 15)  # Weekly frequency should create 15 sessions

    # Test the lesson frequency for biweekly bookings.
    @patch('request_handler.views.accept_request.datetime')
    def test_biweekly_booking_frequency(self, mock_datetime):
        self.lesson_request.frequency = 'Biweekly'
        self.lesson_request.day2 = self.day_friday
        self.lesson_request.save()

        mock_datetime.today.return_value = datetime(2024, 8, 1)
        mock_datetime.combine.side_effect = lambda d, t: datetime.combine(d, t)
        self.client.post(reverse('accept_request', kwargs={'request_id': self.lesson_request.id}))

        # Check the number of sessions created
        bookings = Booking.objects.all()
        self.assertEqual(bookings.count(), 30)  # Biweekly frequency should create 30 sessions
        bookings = bookings[:5]
        # Ensure the first 5 dates are correct
        dates = ["2024-09-02", "2024-09-06", "2024-09-09", "2024-09-13", "2024-09-16"]
        matches = True
        for i in bookings:
            if str(i.date) != dates[0]:
                matches = False
            dates.pop(0)
        self.assertTrue(matches)

    # Test the lesson frequency for biweekly bookings with the first date being before the second
    @patch('request_handler.views.accept_request.datetime')
    def test_biweekly_booking_frequency_later_date(self, mock_datetime):
        self.lesson_request.frequency = 'Biweekly'
        self.lesson_request.day = self.day_friday
        self.lesson_request.day2 = self.day_monday

        self.lesson_request.save()

        mock_datetime.today.return_value = datetime(2024, 8, 1)
        mock_datetime.combine.side_effect = lambda d, t: datetime.combine(d, t)
        response = self.client.post(reverse('accept_request', kwargs={'request_id': self.lesson_request.id}))

        # Check the number of sessions created
        bookings = Booking.objects.all()
        self.assertEqual(bookings.count(), 30)  # Biweekly frequency should create 30 sessions

        bookings = bookings[:5]
        # Ensure the first 5 dates are correct
        dates = ["2024-09-06", "2024-09-09", "2024-09-13", "2024-09-16", "2024-09-20"]
        matches = True
        for i in bookings:
            if str(i.date) != dates[0]:
                matches = False
            dates.pop(0)

        self.assertEqual(matches, True)

    # Test the lesson frequency for fortnightly bookings.
    @patch('request_handler.views.accept_request.datetime')
    def test_fortnightly_booking_frequency(self, mock_datetime):
        self.lesson_request.frequency = 'Fortnightly'
        self.lesson_request.save()

        mock_datetime.today.return_value = datetime(2024, 8, 1)
        mock_datetime.combine.side_effect = lambda d, t: datetime.combine(d, t)
        response = self.client.post(reverse('accept_request', kwargs={'request_id': self.lesson_request.id}))

        # Check the number of sessions created
        bookings = Booking.objects.all()
        self.assertEqual(bookings.count(), 7)  # Fortnightly frequency should create 7 sessions

    # Test lesson frequency and redirect for lesson requests with no matching frequency
    @patch('request_handler.views.accept_request.datetime')
    def test_lesson_frequency_no_match(self, mock_datetime):
        self.lesson_request.frequency = 'Monthly'
        self.lesson_request.save()
        mock_datetime.today.return_value = datetime(2024, 8, 1)
        mock_datetime.combine.side_effect = lambda d, t: datetime.combine(d, t)
        response = self.client.post(reverse('accept_request', kwargs={'request_id': self.lesson_request.id}))
        # Check the number of sessions created
        bookings = Booking.objects.all()
        self.assertEqual(bookings.count(), 0)
        self.assertRedirects(response, reverse('view_requests'), status_code=302, target_status_code=200)

    # Test the january term bookings in January
    @patch('request_handler.views.accept_request.datetime')
    def test_january_request_in_january(self, mock_datetime):
        self.lesson_request.term = 'January'
        self.lesson_request.save()
        mock_datetime.today.return_value = datetime(2025, 1, 1)
        mock_datetime.combine.side_effect = lambda d, t: datetime.combine(d, t)
        response = self.client.post(reverse('accept_request', kwargs={'request_id': self.lesson_request.id}))
        # Check the number of sessions created
        bookings = Booking.objects.all()
        self.assertEqual(bookings.count(), 15)

        # Test the january term bookings in September

    @patch('request_handler.views.accept_request.datetime')
    def test_january_requests_in_september(self, mock_datetime):
        self.lesson_request.term = 'January'
        self.lesson_request.save()
        mock_datetime.today.return_value = datetime(2024, 9, 1)
        mock_datetime.combine.side_effect = lambda d, t: datetime.combine(d, t)
        response = self.client.post(reverse('accept_request', kwargs={'request_id': self.lesson_request.id}))
        # Check the number of sessions created
        bookings = Booking.objects.all()
        self.assertEqual(bookings.count(), 15)

        # Test the May term bookings in September

    @patch('request_handler.views.accept_request.datetime')
    def test_may_requests_in_september(self, mock_datetime):
        self.lesson_request.term = 'May'
        self.lesson_request.save()
        mock_datetime.today.return_value = datetime(2024, 9, 1)
        mock_datetime.combine.side_effect = lambda d, t: datetime.combine(d, t)
        response = self.client.post(reverse('accept_request', kwargs={'request_id': self.lesson_request.id}))
        # Check the number of sessions created
        bookings = Booking.objects.all()
        self.assertEqual(bookings.count(), 15)

        # Test the May term bookings in May

    @patch('request_handler.views.accept_request.datetime')
    def test_may_requests_in_may(self, mock_datetime):
        self.lesson_request.term = 'May'
        self.lesson_request.save()
        mock_datetime.today.return_value = datetime(2025, 5, 1)
        mock_datetime.combine.side_effect = lambda d, t: datetime.combine(d, t)
        response = self.client.post(reverse('accept_request', kwargs={'request_id': self.lesson_request.id}))
        # Check the number of sessions created
        bookings = Booking.objects.all()
        self.assertEqual(bookings.count(), 15)

        # Test a term that doesn't match

    @patch('request_handler.views.accept_request.datetime')
    def test_term_has_no_match(self, mock_datetime):
        self.lesson_request.term = 'December'
        self.lesson_request.save()
        mock_datetime.today.return_value = datetime(2024, 9, 1)
        mock_datetime.combine.side_effect = lambda d, t: datetime.combine(d, t)
        response = self.client.post(reverse('accept_request', kwargs={'request_id': self.lesson_request.id}))
        # Check the number of sessions created
        bookings = Booking.objects.all()
        self.assertEqual(bookings.count(), 0)
        self.assertRedirects(response, reverse('view_requests'), status_code=302, target_status_code=200)

    # Test that an error during booking is caught and handled.
    def test_error_handling_booking_creation(self):
        # Mock the creation of bookings to raise an exception
        with patch('calendar_scheduler.models.Booking.objects.create', side_effect=Exception('Error creating booking')):
            response = self.client.post(reverse('accept_request', kwargs={'request_id': self.lesson_request.id}))

        self.assertRedirects(response, reverse('view_requests'))

    # Test that a non-existent request should fail.
    def test_request_not_found(self):
        response = self.client.post(reverse('accept_request', args=[99999]))
        self.assertEqual(response.status_code, 404)

    # Test that another user cannot accept a request.
    def test_user_not_admin(self):
        other_user = User.objects.create_user(username="@other_user", email="other_user@example.com",
                                              password="Password123")
        self.client.login(username="@other_user", password="Password123")

        response = self.client.post(reverse('accept_request', args=[self.lesson_request.id]))
        self.assertEqual(response.status_code, 404)

    def test_corner_case_for_match_frequency(self):
        self.lesson_request.frequency = "INVALID"
        self.lesson_request.save()
        self.client.force_login(self.tutor)
        response = self.client.post(reverse('accept_request', args=[self.lesson_request.id]))
        self.assertRedirects(response, reverse('view_requests'), status_code=302, target_status_code=200)

    # Test lesson request identifiers when there are previous requests
    def test_pre_lesson_identifiers(self):
        # Post the current lesson request
        self.client.post(reverse('accept_request', args=[self.lesson_request.id]))
        # Now try to post another
        self.lesson_request = Request.objects.create(
            id=2,
            allocated=True,
            tutor=self.tutor,
            student=self.student,
            term="September",
            day=self.day_monday,
            frequency="Weekly",
            duration=60,
            is_recurring=False,
            knowledge_area="Robotics",
            venue=self.venue_online,
        )
        response = self.client.post(reverse('accept_request', args=[2]))
        bookings = Booking.objects.filter(tutor=self.tutor)
        self.assertEqual(len(bookings), 30)  # Weekly = 15 sessions so we need double 
        with self.assertRaises(Request.DoesNotExist):
            Request.objects.get(id=self.lesson_request.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('view_requests'))

    def test_match_term_default_case(self):
        self.lesson_request.frequency = "INVALID"
        self.lesson_request.save()
        date = datetime(2025,5,4,12,0,0)
        with self.assertRaises(ValueError):
            match_lesson_frequency(self.lesson_request,date)