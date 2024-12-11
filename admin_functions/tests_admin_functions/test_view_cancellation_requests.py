from datetime import date

from django.test import TestCase
from django.urls import reverse

from calendar_scheduler.models import Booking
from user_system.fixtures import create_test_users
from user_system.models.user_model import User


class ViewCancellationRequestsTestCase(TestCase):
    def setUp(self):
        create_test_users.create_test_users()
        self.student = User.objects.get(user_type=User.ACCOUNT_TYPE_STUDENT)
        self.admin = User.objects.get(user_type=User.ACCOUNT_TYPE_ADMIN)
        self.tutor = User.objects.get(user_type=User.ACCOUNT_TYPE_TUTOR)

        self.booking_sep = Booking.objects.create(  # September term booking
            student=self.student,
            tutor=self.tutor,
            lesson_identifier="1",
            date=date(2024, 12, 3),
            cancellation_requested=True
        )

    def test_post_not_allowed(self):
        self.client.login(username=self.admin.username, password='Password123')
        response = self.client.post(reverse('view_cancellation_requests'))
        self.assertEqual(response.status_code, 405)

    def test_unauthenticated_user_cannot_view_requests(self):
        response = self.client.get(reverse('view_cancellation_requests'), follow=True)
        self.assertRedirects(response, reverse('log_in'), status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'log_in.html')

    def test_post_requests_not_accepted(self):
        self.client.login(username=self.admin.username, password='Password123')
        response = self.client.post(reverse('view_cancellation_requests'))
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.content, b'Not Allowed')

    def test_non_admin_not_allowed(self):
        self.client.login(username=self.student.username, password='Password123')
        response = self.client.get(reverse('view_cancellation_requests'))
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'permission_denied.html')

    def test_cancellation_requests_in_view(self):
        self.client.login(username=self.admin.username, password='Password123')
        response = self.client.get(reverse('view_cancellation_requests'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'view_cancellation_requests.html')
