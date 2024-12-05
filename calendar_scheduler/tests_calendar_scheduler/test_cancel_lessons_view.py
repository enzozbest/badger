from django.test import TestCase
from django.urls import reverse
from user_system.models import User
from calendar_scheduler.models import Booking
from datetime import datetime, timedelta, date

""" Class to represent the cancelling of lessons

This class is used as a view for the website. It creates multiple bookings and attempts to delete them in multiple ways
and by multiple users, as the functionality works in the cancel_lessons view.
"""

class CancelLessonsViewTests(TestCase):
    def setUp(self):
        # Create users
        from user_system.fixtures import create_test_users
        create_test_users.create_test_user()
        self.tutor = User.objects.get(user_type=User.ACCOUNT_TYPE_TUTOR)
        self.student = User.objects.get(user_type=User.ACCOUNT_TYPE_STUDENT)

        self.booking_sep = Booking.objects.create( # September term booking
            student=self.student,
            tutor=self.tutor,
            start="2024-12-03 10:00:00",
            end="2024-12-03 11:00:00",
            lesson_identifier="1",
            date=date(2024, 12, 3)
        )

        self.booking_jan = Booking.objects.create( # January term booking
            student=self.student,
            tutor=self.tutor,
            start="2025-03-03 10:00:00",
            end="2025-03-03 11:00:00",
            lesson_identifier="2",
            date=date(2025, 3, 3)
        )

        self.booking_may = Booking.objects.create( # May term booking
            student=self.student,
            tutor=self.tutor,
            start="2025-06-03 10:00:00",
            end="2025-06-03 11:00:00",
            lesson_identifier="3",
            date=date(2025, 6, 3)
        )

        self.booking_recurring = Booking.objects.create(  # Recurring booking
            student=self.student,
            tutor=self.tutor,
            start="2025-02-03 10:00:00",
            end="2025-07-03 11:00:00",
            lesson_identifier="4",
            date=date(2025, 2, 3),
            is_recurring = True
        )

        self.client.login(username=self.tutor.username, password='Password123')
        self.student_client = self.client

    # Test that tutor sees the correct cancellation page.
    def test_tutor_get_cancel_lessons(self):
        response = self.client.get(reverse('tutor_cancel_lessons'),
                                   {'day': 3, 'month': 12, 'year': 2024, 'lesson': '1'})
        self.assertTemplateUsed(response, 'tutor_cancel_lessons.html')

        # Test if the date is more than 2 weeks away
        future_date = (datetime(2024, 12, 3) + timedelta(days=20)).date()  # More than 2 weeks ahead
        response = self.client.get(reverse('tutor_cancel_lessons'),
                                   {'day': future_date.day, 'month': future_date.month, 'year': future_date.year,
                                    'lesson': '1'})
        self.assertContains(response,
                            'Click below to cancel your individual lesson')  # When close_date is False

        # Test if the date is within 2 weeks
        close_date = (datetime(2024, 12, 3) + timedelta(days=5)).date()  # Within 2 weeks
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

    # Test that an admin can cancel lessons from the tutor/student calendar.
    def test_permission_denied_for_non_student_or_tutor(self):
        admin = User.objects.create_user(username="@admin", password="Password123", email="admin@example.com")
        admin = User.objects.get(user_type=User.ACCOUNT_TYPE_ADMIN)

        # Log in as admin (who should have access to this view)
        self.client.login(username="@admin", password="Password123")
        response = self.client.get(reverse('tutor_cancel_lessons'),
                                   {'day': 3, 'month': 12, 'year': 2024, 'lesson': '1'})

        self.assertTemplateUsed(response, 'student_cancel_lessons.html')
        self.assertEqual(response.status_code, 200)