from datetime import datetime
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from request_handler.models import Venue
from user_system.fixtures.create_test_users import create_test_users
from user_system.models import Day, User

INVALID_REQUEST_ID = 999


class TestViews(TestCase):
    def setUp(self):
        create_test_users()
        self.monday, _ = Day.objects.get_or_create(day='Monday')
        self.online, _ = Venue.objects.get_or_create(venue='Online')
        self.student = User.objects.get(username='@charlie')
        self.tutor = User.objects.get(username='@janedoe')
        self.student = User.objects.get(username='@charlie')

        self.url = reverse('create_request')

    def test_user_can_see_rqeuest_creation_page(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_create_request_with_valid_data(self):
        self.client.force_login(self.student)
        data = {
            'term': 'January',
            'knowledge_area': 'Scala',
            'frequency': 'Biweekly',
            'duration': '1',
            'venue_preference': [self.online.pk],
        }
        response = self.client.post(self.url, data, follow=True)
        self.assertRedirects(response, reverse('request_success'), status_code=302, target_status_code=200)

    def test_create_request_with_invalid_data(self):
        self.client.login(username='@charlie', password='Password123')
        # Blank 'term' field!
        data = {
            'term': '',
            'knowledge_area': 'Scala',
            'frequency': 'Weekly',
            'duration': '1',
            'venue_preference': [self.online.id, ]
        }
        self.client.post(self.url, data)
        self.assertRaises(ValueError)

    def test_tutor_cannot_create_request_get(self):
        self.client.login(username='@janedoe', password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'permission_denied.html')

    def test_tutor_cannot_create_request_post(self):
        self.client.login(username='@janedoe', password='Password123')
        response = self.client.post(self.url, follow=True)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'permission_denied.html')

    def test_unauthenticated_user_cannot_create_request_get(self):
        response = self.client.get(self.url, follow=True)
        expected_url = f'{reverse("log_in")}?next={reverse("create_request")}'
        self.assertRedirects(response, expected_url, status_code=302, target_status_code=200)

    def test_unauthenticated_user_cannot_create_request_post(self):
        response = self.client.post(self.url, follow=True)
        expected_url = f'{reverse("log_in")}?next={reverse("create_request")}'
        self.assertRedirects(response, expected_url, status_code=302, target_status_code=200)

    def test_form_late_request_redirect(self):
        self.client.login(username='@charlie', password='Password123')
        data = {
            'term': '',
            'knowledge_area': 'Scala',
            'frequency': 'Weekly',
            'duration': '1',
            'venue_preference': [self.online.id]
        }
        # Purposefully choosing a late term
        if datetime.now().month >= 1 and datetime.now().month < 5:
            data['term'] = 'January'
        elif datetime.now().month > 8 and datetime.now().month <= 12:
            data['term'] = 'September'
        elif datetime.now().month < 9:
            data['term'] = 'May'

        url = reverse('create_request')
        response = self.client.post(url, data, follow=True)
        self.assertRedirects(response, reverse('processing_late_request'), status_code=302, target_status_code=200)

    @patch('request_handler.models.Request.save', side_effect=Exception("Database error"))
    def test_post_handles_exception(self, mock_save):
        self.client.force_login(self.student)
        data = {
            'knowledge_area': 'Python',
            'term': 'May',
            'frequency': 'Weekly',
            'duration': '2',
            'venue_preference': [self.online.id],
        }
        response = self.client.post(self.url, data)
        self.assertContains(response, 'There was an error submitting this form! Database error')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_request.html')
