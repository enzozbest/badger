from datetime import date
from calendar_scheduler.models import Booking
from schedule.models import Calendar
from django.test import TestCase
from user_system.models import User
from django.urls import reverse
from datetime import timedelta
from calendar_scheduler.views.calendar import get_month_days, get_week_days
from user_system.fixtures import create_test_users


""" Classes to represent the calendar and lessons within the calendar

Both classes below (CalendarHelperTests and CalendarViewTests) are used as a view for the website. CalendarHelperTests
tests the helper methods in the calendar view, and CalendarViewTests tests the relevant calendar functionality.
"""

class CalendarHelperTests(TestCase):
    # Tests that the months and their days are retrieved correctly.
    def test_get_month_days(self):
        # Test for a standard month (e.g., November 2024)
        november_days = get_month_days(2024, 11)
        self.assertEqual(len(november_days), 5)  # November 2024 has 5 weeks
        self.assertEqual(november_days[0][0], '')  # First week starts on Friday (empty days before)

        # Test for February in a leap year (2024)
        february_days = get_month_days(2024, 2)
        self.assertEqual(len(february_days), 5)  # February 2024 calendar displays 5 weeks
        self.assertEqual(february_days[-1][-1], 29)  # Last day is the 29th

        # Test for December
        december_days = get_month_days(2024, 12)
        self.assertEqual(len(december_days), 6)  # Displays 6 weeks (overruns into Nov and Jan)

    # Tests that the week's days are retrieved correctly.
    def test_get_week_days(self):
        week_days = get_week_days()
        self.assertEqual(len(week_days), 7)  # Should return 7 days
        today = date.today()
        self.assertEqual(week_days[0], today - timedelta(days=today.weekday()))  # Start of the week

class CalendarViewTests(TestCase):
    def setUp(self):
        # Create users
        create_test_users.create_test_users()
        self.tutor = User.objects.get(user_type=User.ACCOUNT_TYPE_TUTOR)
        self.student = User.objects.get(user_type=User.ACCOUNT_TYPE_STUDENT)
        self.admin = User.objects.create_user(username="@admin", password="Password123", email="admin@example.com", user_type=User.ACCOUNT_TYPE_ADMIN)

        # Ensure the slug doesn't already exist
        self.calendar, created = Calendar.objects.get_or_create(
            slug='tutor',
            defaults={'name': 'Tutor Calendar'}
        )

        self.booking_tutor = Booking.objects.create(
            tutor=self.tutor,
            date=date.today(),
            lesson_identifier='1'
        )
        self.booking_student = Booking.objects.create(
            student=self.student,
            date=date.today(),
            lesson_identifier='2'
        )

    # Test that the month is updated correctly if the previous button is clicked.
    def test_month_less_than_one(self):
        self.client.login(username=self.tutor.username, password='Password123')

        response = self.client.get(reverse('tutor_calendar'), {'year': 2024, 'month': 0})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '2023')  # The year should now be 2023
        self.assertContains(response, '12')  # The corrected month should now be December (12)

    # Test that the month is updated correctly if the next button is clicked.
    def test_month_greater_than_twelve(self):
        self.client.login(username=self.tutor.username, password='Password123')

        response = self.client.get(reverse('tutor_calendar'), {'year': 2023, 'month': 13})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '2024')  # The year should now be 2024
        self.assertContains(response, '1')  # The corrected month should now be January (1)

    # Test that the tutor can see the calendar.
    def test_tutor_calendar_view_access(self):
        self.client.login(username=self.tutor.username, password='Password123')
        response = self.client.get(reverse('tutor_calendar'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor_calendar.html')
        self.assertContains(response, self.booking_tutor.lesson_identifier)

    # Test that the student can see the calendar.
    def test_student_calendar_view_access(self):
        self.client.login(username=self.student.username, password='Password123')
        response = self.client.get(reverse('student_calendar'))  # Adjust the name to match your URL pattern
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_calendar.html')
        self.assertContains(response, self.booking_student.lesson_identifier)  # Verify booking appears in the calendar

    # Test that a student cannot see a tutor's calendar.
    def test_tutor_calendar_no_permission(self):
        self.client.login(username=self.student.username, password='Password123')
        response = self.client.get(reverse('tutor_calendar'))
        self.assertEqual(response.status_code, 401)  # Permission denied for students

    # Test that a tutor cannot see a student's calendar.
    def test_student_calendar_no_permission(self):
        self.client.login(username=self.tutor.username, password='Password123')
        response = self.client.get(reverse('student_calendar'))
        self.assertEqual(response.status_code, 401)  # Permission denied for tutors

    # Test to respond if a calendar is not found for a tutor.
    def test_tutor_calendar_not_found(self):
        self.client.login(username=self.tutor.username, password='Password123')
        Calendar.objects.filter(slug='tutor').delete()
        response = self.client.get(reverse('tutor_calendar'))
        self.assertEqual(response.status_code, 404)

    # Test to respond if a calendar is not found for a student.
    def test_student_calendar_not_found(self):
        self.client.login(username=self.student.username, password='Password123')
        Calendar.objects.filter(slug='tutor').delete()
        response = self.client.get(reverse('student_calendar'))
        self.assertEqual(response.status_code, 404)

    # Test that the admin can see the calendar.
    def test_admin_calendar_view_access(self):
        self.client.login(username="@admin", password='Password123')
        response = self.client.get(reverse('student_calendar'))  # Adjust the name to match your URL pattern
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_calendar.html')
        self.assertContains(response, self.booking_student.lesson_identifier)  # Verify booking appears in the calendar

    # Test if that calendar is not found for admin users.
    def test_calendar_not_found_admin(self):
        self.client.login(username="@admin", password='Password123')
        Calendar.objects.filter(slug='tutor').delete()
        response = self.client.get(reverse('student_calendar'))
        self.assertEqual(response.status_code, 404)

    # Test that the admin can see all lessons in the calendar. DONT WANT IT LIKE THIS ANYMORE, WANT INDIVIDUAL CALENDARS
    def test_admin_calendar_view_all_events(self):
        self.client.login(username=self.admin.username, password='Password123')
        # Simulate viewing the calendar for today
        response = self.client.get(reverse('tutor_calendar'), {'year': 2024, 'month': 12, 'day': date.today().day})
        self.assertEqual(response.status_code, 200)
        # Check if bookings are present in the response
        self.assertContains(response, self.booking_tutor.lesson_identifier)
        self.assertContains(response, self.booking_student.lesson_identifier)
        self.assertTemplateUsed(response, 'tutor_calendar.html')
