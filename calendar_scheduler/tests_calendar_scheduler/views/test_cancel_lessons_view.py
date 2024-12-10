from datetime import date, datetime, timedelta
from unittest.mock import patch

from django.test import Client, TestCase
from django.urls import reverse

from calendar_scheduler.models import Booking
from calendar_scheduler.views.cancel_lessons import cancel_day, cancel_recurring, cancel_term
from user_system.fixtures import create_test_users
from user_system.models.user_model import User

""" Class to represent the cancelling of lessons

This class is used as a view for the website. It creates multiple bookings and attempts to delete them in multiple ways
and by multiple users, as the functionality works in the cancel_lessons view.
"""


class CancelLessonsViewTests(TestCase):
    def setUp(self):
        # Create users
        self.client = Client()
        create_test_users.create_test_users()
        self.tutor = User.objects.get(user_type=User.ACCOUNT_TYPE_TUTOR)
        self.student = User.objects.get(user_type=User.ACCOUNT_TYPE_STUDENT)

        self.booking_sep = Booking.objects.create(  # September term booking
            student=self.student,
            tutor=self.tutor,
            lesson_identifier="1",
            date=date(2024, 12, 3)
        )

        self.booking_jan = Booking.objects.create(  # January term booking
            student=self.student,
            tutor=self.tutor,
            lesson_identifier="2",
            date=date(2025, 3, 3)
        )

        self.booking_may = Booking.objects.create(  # May term booking
            student=self.student,
            tutor=self.tutor,
            lesson_identifier="3",
            date=date(2025, 6, 3)
        )

        self.booking_recurring = Booking.objects.create(  # Recurring booking
            student=self.student,
            tutor=self.tutor,
            lesson_identifier="4",
            date=date(2025, 2, 3),
            is_recurring=True
        )

        self.booking = Booking.objects.create(
            lesson_identifier="1",
            date=date(2024, 12, 15),
            cancellation_requested=False
        )

        self.client.login(username=self.tutor.username, password='Password123')
        self.student_client = self.client

    # Test that tutor sees the correct cancellation page.
    def test_tutor_get_cancel_lessons(self):
        response = self.client.get(reverse('tutor_cancel_lessons'),
                                   {'day': 3, 'month': 12, 'year': 2024, 'lesson': '1'})
        self.assertTemplateUsed(response, 'tutor_cancel_lessons.html')

        # Test if the date is more than 2 weeks away
        future_date = (datetime(2035, 12, 3) + timedelta(days=20)).date()  # More than 2 weeks ahead
        response = self.client.get(reverse('tutor_cancel_lessons'),
                                   {'day': future_date.day, 'month': future_date.month, 'year': future_date.year,
                                    'lesson': '1'})
        self.assertContains(response,
                            'Click below to cancel all lessons for your term')

        # Test if the date is within 2 weeks
        close_date = (datetime(2024, 11, 5) + timedelta(days=5)).date()  # Within 2 weeks
        response = self.client.get(reverse('tutor_cancel_lessons'),
                                   {'day': close_date.day, 'month': close_date.month, 'year': close_date.year,
                                    'lesson': '1'})
        self.assertContains(response,
                            'Click below to cancel all lessons for your term')  # When close_date is True

    # Test that a student can see the correct cancellation page.
    def test_student_get_cancel_lessons(self):
        self.client.login(username=self.student.username, password='Password123')
        response = self.client.get(reverse('student_cancel_lessons'),
                                   {'day': 3, 'month': 12, 'year': 2024, 'lesson': '1'})
        self.assertTemplateUsed(response, 'student_cancel_lessons.html')

    # Test the POST request for cancelling a specific lesson day for a tutor.
    def test_post_cancel_day_tutor(self):
        response = self.client.post(reverse('tutor_cancel_lessons'), {
            'day': 3,
            'month': 12,
            'year': 2024,
            'lesson': '1',
            'cancellation': 'day'
        })

        # Ensure the lesson is deleted from the database
        lesson = Booking.objects.filter(lesson_identifier="1", date=date(2024, 12, 3))
        self.assertEqual(len(lesson), 0)
        self.assertRedirects(response, reverse('tutor_calendar'))

    # Test the POST request for cancelling a specific lesson day for a student.
    def test_post_cancel_day_student(self):
        self.client.login(username=self.student.username, password='Password123')
        response = self.client.post(reverse('tutor_cancel_lessons'), {
            'day': 3,
            'month': 12,
            'year': 2024,
            'lesson': '1',
            'cancellation': 'day'
        })

        # Ensure the lesson is deleted from the database
        lesson = Booking.objects.filter(lesson_identifier="1", date=date(2024, 12, 3))
        self.assertEqual(len(lesson), 0)
        self.assertRedirects(response, reverse('student_calendar'))

    # Test the POST request for cancelling all lessons in the September term.
    def test_post_cancel_term_sep(self):
        response = self.client.post(reverse('tutor_cancel_lessons'), {
            'day': 3,
            'month': 12,
            'year': 2024,
            'lesson': '1',
            'cancellation': 'term'
        })

        # Ensure the lessons for the term are deleted
        lessons_in_december = Booking.objects.filter(lesson_identifier="1", date__month=12)
        self.assertEqual(len(lessons_in_december), 0)

    # Test the POST request for cancelling all lessons in the January term.
    def test_post_cancel_term_jan(self):
        response = self.client.post(reverse('tutor_cancel_lessons'), {
            'day': 3,
            'month': 3,
            'year': 2025,
            'lesson': '2',
            'cancellation': 'term'
        })

        # Ensure the lessons for the term are deleted
        lessons_in_march = Booking.objects.filter(lesson_identifier="2", date__month=3)
        self.assertEqual(len(lessons_in_march), 0)

    # Test the POST request for cancelling all lessons in the May term.
    def test_post_cancel_term_may(self):
        response = self.client.post(reverse('tutor_cancel_lessons'), {
            'day': 3,
            'month': 6,
            'year': 2024,
            'lesson': '3',
            'cancellation': 'term'
        })

        # Ensure the lessons for the term are deleted
        lessons_in_june = Booking.objects.filter(lesson_identifier="3", date__month=6)
        self.assertEqual(len(lessons_in_june), 0)

    # Test the POST request for cancelling recurring lessons.
    def test_post_cancel_recurring(self):
        response = self.client.post(reverse('tutor_cancel_lessons'), {
            'day': 3,
            'month': 2,
            'year': 2025,
            'lesson': '4',
            'cancellation': 'recurring'
        })

        # Ensure all lessons with the same lesson_identifier are deleted (recurring)
        recurring_lessons = Booking.objects.filter(lesson_identifier="4")
        self.assertEqual(len(recurring_lessons), 0)

    # Test that a request can be made for cancellation.
    def test_post_request_cancellation(self):
        self.client.login(username=self.student.username, password='Password123')
        response = self.client.post(reverse('student_cancel_lessons'), {
            'day': 15,
            'month': 12,
            'year': 2024,
            'lesson': '1',
            'cancellation': 'request',
        })
        self.assertEqual(response.status_code, 302)
        self.booking.refresh_from_db()
        self.assertTrue(self.booking.cancellation_requested)

    # Test that an admin can cancel lessons from the tutor/student calendar.
    def test_permission_denied_for_non_student_or_tutor(self):
        admin = User.objects.create_user(username="@admin", password="Password123", email="admin@example.com")
        admin = User.objects.get(user_type=User.ACCOUNT_TYPE_ADMIN)

        # Log in as admin (who should not have access to this view)
        self.client.login(username="@admin", password="Password123")
        response = self.client.get(reverse('tutor_cancel_lessons'),
                                   {'day': 3, 'month': 12, 'year': 2024, 'lesson': '1'})

        self.assertTemplateUsed(response, 'permission_denied.html')
        self.assertEqual(response.status_code, 401)

    # Test that the cancel_day helper method works.
    def test_cancel_day_success(self):
        cancel_day('1', date(2024, 12, 15))
        with self.assertRaises(Booking.DoesNotExist):
            Booking.objects.get(lesson_identifier='1', date=date(2024, 12, 15))

    def test_cancel_day_not_found(self):
        response = cancel_day('1', date(2024, 12, 20))
        self.assertEqual(response.status_code, 404)

    # Test that the cancel_term helper method works.
    def test_cancel_term(self):
        cancel_term('1', '12')
        self.assertFalse(Booking.objects.filter(lesson_identifier='1').exists())

    # Test that the cancel recurring helper method works.
    def test_cancel_recurring(self):
        cancel_recurring('1')
        self.assertFalse(Booking.objects.filter(lesson_identifier='1').exists())


""" Class to represent the cancelling of lessons for admins

This class is used as a view for the website. It creates multiple bookings and attempts to delete them in multiple ways
through an admin (and as other forbidden users), as the functionality works in the cancel_lessons view.
"""


class AdminCancelLessonsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(username='admin', password='password', user_type="Admin")
        self.client.login(username='admin', password='password')

        test_date = date.today() + timedelta(days=10)
        self.booking_date = test_date
        self.booking = Booking.objects.create(
            lesson_identifier="1",
            date=test_date,
            cancellation_requested=False
        )

    # Test that the admin can see the cancellation page.
    def test_get_admin_cancel_lessons(self):
        # Perform a GET request as an admin
        response = self.client.get('/admins/calendar/cancel/', {
            'day': self.booking_date.day,
            'month': self.booking_date.month,
            'year': self.booking_date.year,
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_cancel_lessons.html')

    # Test that the admin can cancel a day lesson.
    def test_post_cancel_day(self):
        response = self.client.post('/admins/calendar/cancel/', {
            'lesson': '1',
            'cancellation': 'day',
            'day': self.booking_date.day,
            'month': self.booking_date.month,
            'year': self.booking_date.year,
        })
        self.assertEqual(response.status_code, 302)  # Redirect to view_all_users
        self.assertFalse(Booking.objects.filter(lesson_identifier="1", date=self.booking_date).exists())

    # Test that the admin can cancel all the lessons in a term.
    def test_post_cancel_term(self):
        response = self.client.post('/admins/calendar/cancel/', {
            'lesson': '1',
            'cancellation': 'term',
            'month': self.booking_date.month,
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Booking.objects.filter(lesson_identifier="1").exists())

    # Test for an invalid cancellation type.
    def test_post_invalid_cancellation_type(self):
        response = self.client.post('/admins/calendar/cancel/', {
            'lesson': '1',
            'cancellation': 'invalid',
        })
        self.assertEqual(response.status_code, 400)

    # Test that an admin can cancel recurring lessons.
    def test_post_cancel_recurring(self):
        response = self.client.post('/admins/calendar/cancel/', {
            'lesson': '1',
            'cancellation': 'recurring',
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Booking.objects.filter(lesson_identifier="1").exists())

    # Test when the close_date is false.
    def test_close_date_false(self):
        test_date_2 = date.today() + timedelta(days=20)
        self.booking_2 = Booking.objects.create(
            lesson_identifier="2",
            date=test_date_2,
            cancellation_requested=False
        )
        response = self.client.get('/admins/calendar/cancel/', {
            'day': test_date_2.day,
            'month': test_date_2.month,
            'year': test_date_2.year,
            'lesson': 2,  # Dummy lesson identifier
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_cancel_lessons.html')

    # Test the value error in the admin cancel lessons view.
    def test_post_cancel_day_value_error(self):
        invalid_date = date.today() + timedelta(days=10)
        response = self.client.post('/admins/calendar/cancel/', {
            'lesson': '999999',  # Non-existent lesson_id
            'cancellation': 'day',
            'day': invalid_date.day,
            'month': invalid_date.month,
            'year': invalid_date.year,
        })
        self.assertEqual(response.status_code, 500)
        self.assertIn("No booking found for lesson_id", response.content.decode())

    # Test the exception in the admin cancel lessons view.
    def test_post_generic_exception(self):
        with patch('calendar_scheduler.models.Booking.objects.get', side_effect=Exception("Unexpected error")):
            response = self.client.post('/admins/calendar/cancel/', {
                'lesson': '1',
                'cancellation': 'day',
                'day': self.booking_date.day + 1,
                'month': self.booking_date.month,
                'year': self.booking_date.year,
            })
        expected_date = (self.booking_date + timedelta(days=1)).strftime('%Y-%m-%d')
        self.assertEqual(response.status_code, 500)
        self.assertIn(f"Error processing cancellation: No booking found for lesson_id: 1 on {expected_date}",
                      response.content.decode())
