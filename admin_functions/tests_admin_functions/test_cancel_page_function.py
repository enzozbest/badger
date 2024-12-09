from django.test import TestCase
from django.urls import reverse
from user_system.models.user_model import User
from calendar_scheduler.models import Booking
from datetime import date
import random
import string

def generate_unique_email():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10)) + '@example.com'

class ViewCancellationRequestsTestCase(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin', email=generate_unique_email(), password='password', user_type=User.ACCOUNT_TYPE_ADMIN)
        self.student = User.objects.create_user(username='student', email=generate_unique_email(), password='password', user_type=User.ACCOUNT_TYPE_STUDENT)
        self.tutor = User.objects.create_user(username='tutor', email=generate_unique_email(), password='password', user_type=User.ACCOUNT_TYPE_TUTOR)

        self.booking_sep = Booking.objects.create(
            student=self.student,
            tutor=self.tutor,
            start="2024-12-03 10:00:00",
            end="2024-12-03 11:00:00",
            lesson_identifier="1",
            date=date(2024, 12, 3),
            cancellation_requested=True
        )

    def test_filter_by_student_name(self):
        self.client.login(username=self.admin.username, password='password')
        response = self.client.get(reverse('view_cancellation_requests') + '?search=' + self.student.first_name)
        self.assertContains(response, self.student.first_name)
        self.assertNotContains(response, 'No results found')

    def test_filter_by_tutor_name(self):
        self.client.login(username=self.admin.username, password='password')
        response = self.client.get(reverse('view_cancellation_requests') + '?search=' + self.tutor.first_name)
        self.assertContains(response, self.tutor.first_name)
        self.assertNotContains(response, 'No results found')

    def test_filter_by_date(self):
        self.client.login(username=self.admin.username, password='password')
        response = self.client.get(reverse('view_cancellation_requests') + '?search=Dec')
        self.assertContains(response, 'Dec')

    def test_sorting_by_column(self):
        self.client.login(username=self.admin.username, password='password')

        response = self.client.get(reverse('view_cancellation_requests') + '?sort=id')
        self.assertContains(response, 'ID')
        self.assertIn('▲', response.content.decode())

        response = self.client.get(reverse('view_cancellation_requests') + '?sort=student__first_name')
        self.assertContains(response, 'Student')
        self.assertIn('▲', response.content.decode())

    def test_pagination(self):
        self.client.login(username=self.admin.username, password='password')
        
        for i in range(6, 11):
            Booking.objects.create(
                student=self.student,
                tutor=self.tutor,
                start=f"2024-12-{i} 10:00:00",
                end=f"2024-12-{i} 11:00:00",
                lesson_identifier=str(i),
                date=date(2024, 12, i),
                cancellation_requested=True
            )
        
        response = self.client.get(reverse('view_cancellation_requests') + '?page=1')
        self.assertContains(response, 'Page 1 of 2')
        self.assertContains(response, 'ID')


