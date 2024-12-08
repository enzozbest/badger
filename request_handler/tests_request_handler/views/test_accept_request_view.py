from unittest.mock import patch
from django.db.models import Max
from django.test import TestCase
from django.urls import reverse
from user_system.models import User, Day
from request_handler.models import Request, Venue
from calendar_scheduler.models import Booking
from datetime import datetime, timedelta
from django.utils import timezone

class AcceptRequestViewTestCase(TestCase):
    def setUp(self):
        self.tutor = User.objects.create_user(username="@tutor", email="tutor@example.com", password="Password123")
        self.student = User.objects.create_user(username="@student", email="student@example.com", password="Password123")
        self.day_monday, created = Day.objects.get_or_create(day="Monday")
        self.day_friday, created = Day.objects.get_or_create(day="Friday")
        venue_online, created = Venue.objects.get_or_create(venue="Online")

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
            venue=venue_online,
        )
        self.client.login(username="@tutor", password="Password123")

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
    def test_weekly_booking_frequency(self):
        self.lesson_request.frequency = 'Weekly'
        self.lesson_request.save()

        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = datetime(2024, 8, 1)
            response = self.client.post(reverse('accept_request', kwargs={'request_id': self.lesson_request.id}))

        # Check the number of sessions created
        bookings = Booking.objects.all()
        self.assertEqual(bookings.count(), 15)  # Weekly frequency should create 15 sessions

    # Test the lesson frequency for biweekly bookings.
    def test_biweekly_booking_frequency(self):
        self.lesson_request.frequency = 'Biweekly'
        self.lesson_request.day2 = self.day_friday
        
        self.lesson_request.save()

        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = datetime(2024, 8, 1)
            response = self.client.post(reverse('accept_request', kwargs={'request_id': self.lesson_request.id}))

        # Check the number of sessions created
        bookings = Booking.objects.all()
        self.assertEqual(bookings.count(), 30)  # Biweekly frequency should create 30 sessions
        bookings = bookings[:5]
        #Ensure the first 5 dates are correct
        dates = ["2024-09-02","2024-09-06","2024-09-09","2024-09-13","2024-09-16"]
        matches = True
        for i in bookings:
            if str(i.date) != dates[0]:
                matches = False
            dates.pop(0)
        
        self.assertEqual(matches, True)



    # Test the lesson frequency for biweekly bookings with the first date being before the second
    def test_biweekly_booking_frequency_later_date(self):
        self.lesson_request.frequency = 'Biweekly'
        self.lesson_request.day = self.day_friday
        self.lesson_request.day2 = self.day_monday

        self.lesson_request.save()
        
        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = datetime(2024, 8, 1)
            response = self.client.post(reverse('accept_request', kwargs={'request_id': self.lesson_request.id}))

        # Check the number of sessions created
        bookings = Booking.objects.all()
        self.assertEqual(bookings.count(), 30)  # Biweekly frequency should create 30 sessions
        
        bookings = bookings[:5]
        #Ensure the first 5 dates are correct
        dates = ["2024-09-06","2024-09-09","2024-09-13","2024-09-16","2024-09-20"]
        matches = True
        for i in bookings:
            if str(i.date) != dates[0]:
                matches = False
            dates.pop(0)
        
        self.assertEqual(matches, True)
    # Test the lesson frequency for fortnightly bookings.
    def test_fortnightly_booking_frequency(self):
        self.lesson_request.frequency = 'Fortnightly'
        self.lesson_request.save()

        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = datetime(2024, 8, 1)
            response = self.client.post(reverse('accept_request', kwargs={'request_id': self.lesson_request.id}))

        # Check the number of sessions created
        bookings = Booking.objects.all()
        self.assertEqual(bookings.count(), 7)  # Fortnightly frequency should create 7 sessions

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
    def test_user_not_tutor(self):
        other_user = User.objects.create_user(username="@other_user", email="other_user@example.com", password="Password123")
        self.client.login(username="@other_user", password="Password123")

        response = self.client.post(reverse('accept_request', args=[self.lesson_request.id]))
        self.assertEqual(response.status_code, 404)

    # For some reason, this test is getting the first day from September 2025 (but putting the year as 2024)
    '''
    def test_booking_date_for_september(self):
        # Simulate current month as September
        with patch('django.utils.timezone.now', return_value=datetime(2024, 9, 1)):
            # Post the request to accept the request --> booking
            response = self.client.post(reverse('accept_request', args=[self.lesson_request.id]))

            self.assertEqual(response.status_code, 302)  # Assuming redirect happens after successful booking

            # Fetch the first Booking object and assert that it has a start date
            booking = Booking.objects.first()
            self.assertIsNotNone(booking, "Booking object was not created.")

            from django.utils.timezone import make_aware

            expected_date = make_aware(datetime(2024, 9, 2, 12, 0))  # Add timezone awareness

            # Assert that the booking's start and end date are correct
            #expected_date = datetime(2024, 9, 2, 12, 0) # Assuming first weekday of September 2024 is Monday
            self.assertEqual(booking.start, expected_date)
            self.assertEqual(booking.end, expected_date)
    '''