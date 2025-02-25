from datetime import date, timedelta

from django.test import TestCase, override_settings
from django.urls import reverse
from schedule.models import Calendar

from calendar_scheduler.models import Booking
from calendar_scheduler.views.calendar import get_month_days, get_week_days, produce_month_events
from user_system.fixtures import create_test_users
from user_system.models.user_model import User

""" Classes to represent the calendar and lessons within the calendar

Both classes below (CalendarHelperTests and CalendarViewTests) are used as a view for the website. CalendarHelperTests
tests the helper methods in the calendar view (student and tutor view), and CalendarViewTests tests the relevant 
calendar functionality.
"""

@override_settings(USE_AWS_S3=False)
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
        self.admin = User.objects.create_user(username="@admin", password="Password123", email="admin@example.com",
                                              user_type=User.ACCOUNT_TYPE_ADMIN)

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

    # Test exception block in produce_month_events method
    def test_exception_in_produce_month_events(self):
        class MockRequest:
            user = self.student
        mock_request = MockRequest()

        year = 2024
        month = 2
        events = None
        try:
            events = produce_month_events(mock_request, year, month, user_for_calendar=None)
        except ValueError:
            self.fail("produce_month_events raised ValueError unexpectedly!")

        self.assertIsInstance(events, list) # Function should return a list
        self.assertEqual(events, []) # No events expected
        self.assertLessEqual(len(events), 29) # Ensure the loop ran only for valid days

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
        Calendar.objects.filter(slug='student').delete()
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
        Calendar.objects.filter(slug='student').delete()
        response = self.client.get(reverse('student_calendar'))
        self.assertEqual(response.status_code, 404)

    # Test that an admin can view a specific student's calendar.
    def test_admin_view_student_calendar(self):
        self.client.login(username=self.admin.username, password='Password123')
        url = reverse('admin_student_calendar', kwargs={'pk': self.student.pk})
        response = self.client.get(url)

        # Check that the admin can access the calendar and correct template is rendered
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_student_calendar.html')

    # Test that the student view does not allow admins to see a tutor's calendar.
    def test_admin_view_student_calendar_raises_value_error_for_non_student(self):
        self.client.login(username=self.admin.username, password='Password123')
        tutor_user = User.objects.create_user(username='tutor', password='password', user_type=User.ACCOUNT_TYPE_TUTOR)

        url = reverse('admin_student_calendar', kwargs={'pk': tutor_user.pk})

        with self.assertRaises(ValueError):
            self.client.get(url)

    # Test that an admin can view a specific student's calendar.
    def test_admin_view_tutor_calendar(self):
        self.client.login(username=self.admin.username, password='Password123')

        url = reverse('admin_tutor_calendar', kwargs={'pk': self.tutor.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_tutor_calendar.html')

    # Test that the tutor view does not allow admins to see a student's calendar.
    def test_admin_view_tutor_calendar_raises_value_error_for_non_tutor(self):
        self.client.login(username=self.admin.username, password='Password123')

        # Create a tutor user (non-student)
        student_user = User.objects.create_user(username='student', password='password',
                                                user_type=User.ACCOUNT_TYPE_STUDENT)
        url = reverse('admin_tutor_calendar', kwargs={'pk': student_user.pk})

        with self.assertRaises(ValueError):
            self.client.get(url)

    # Test that the ValueError is raised properly.
    def test_admin_view_raises_error_for_unknown_user_type(self):
        self.client.login(username=self.admin.username, password='Password123')

        unknown_user = User.objects.create_user(username='unknown', password='password', user_type='Unknown')
        url = reverse('admin_student_calendar', kwargs={'pk': unknown_user.pk})

        # Ensure that the exception is raised
        with self.assertRaises(ValueError):
            self.client.get(url)

    # Test that the exception works appropriately in the calendar view.
    def test_value_error_handling_in_admin_view(self):
        self.client.login(username=self.admin.username, password='Password123')
        try:
            self.client.get(reverse('admin_student_calendar', kwargs={'pk': 9999}))
        except ValueError as e:
            # Check if ValueError is handled and no traceback is returned
            self.assertIn("Unexpected user type", str(e))
