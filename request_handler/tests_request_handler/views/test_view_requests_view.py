from django.test import TestCase
from django.urls import reverse
from user_system.models import User, Day
from request_handler.models import Request, Venue
from django.forms.models import model_to_dict

INVALID_REQUEST_ID = 999


class viewRequestsTest(TestCase):
    def setUp(self):
        # Set up test user
        self.user = User.objects.create_user(username='@charlie', password='Password123', user_type='Student')
        self.mode_preference = Venue.objects.create(venue="Online")

        self.client.login(username='@charlie', password='Password123')

    # Tests that an unauthenticated user is redirected when attempting to view their lesson requests
    def test_redirect_if_not_logged_in_view_requests(self):
        self.client.logout()
        response = self.client.get(reverse('view_requests'))
        expected_url = f"{reverse('log_in')}?next={reverse('view_requests')}"
        self.assertRedirects(response, expected_url, status_code=302, target_status_code=200)

    # Tests that a logged in user with requests can see them and the data is accurate
    def test_view_requests_populated(self):
        # Request instance belonging to test user
        self.request_instance = Request.objects.create(
            student=self.user,
            knowledge_area='C++',
            term='Easter',
            frequency='Weekly',
            duration='1h',
        )
        self.request_instance.venue_preference.set([self.mode_preference])

        response = self.client.get(reverse('view_requests'))
        self.assertTrue(response.context, {
            'Knowledge_area': 'C++',
            'Term': 'Easter',
            'Frequency': 'Weekly',
            'Duration': '1h',
            'Venue preference': 'Online',
            'Allocated': 'No',
            'Tutor': '-',
        })

    def test_tutor_view_request(self):
        tutor = User.objects.create_user(username='@testtutor', email='test@example.org', password='Password123', user_type='Tutor')
        self.client.login(username='@testtutor', password='Password123')

        self.request_instance = Request.objects.create(
            student=self.user,
            knowledge_area='C++',
            term='Easter',
            frequency='Weekly',
            duration='1h',
            tutor=tutor,
            allocated=True
        )
        self.request_instance.venue_preference.set([self.mode_preference])

        response = self.client.get(reverse('view_requests'))
        self.assertTrue(response.context, {
            'Knowledge_area': 'C++',
            'Term': 'Easter',
            'Frequency': 'Weekly',
            'Duration': '1h',
            'Venue preference': 'Online',
            'Allocated': 'Yes',
            'Tutor': self.request_instance.tutor_name,
        })

    def test_admin_view_request(self):
        admin = User.objects.create_user(username='@admin', email="admin@example.org", password='Password123', user_type='Admin')
        self.client.login(username='@admin', password='Password123')
        student_request = Request.objects.create(
            student=self.user,
            knowledge_area='C++',
            term='Easter',
            frequency='Weekly',
            duration='1h',
            allocated=False
        )
        tutor = User.objects.create_user(username='@testtutor', email='test@example.org', password='Password123',
                                         user_type='Tutor')
        tutor_request = Request.objects.create(
            student=self.user,
            knowledge_area='C++',
            term='Easter',
            frequency='Weekly',
            duration='1h',
            tutor=tutor,
            allocated=True
        )

        response = self.client.get(reverse('view_requests'))
        self.assertTrue(response.context, {model_to_dict(student_request).items().__hash__, model_to_dict(tutor_request).items().__hash__})

    # Tests that a logged in user who requests to view their requests (while having none) does not receive an error
    def test_view_requests_empty(self):
        self.client.login(username='@charlie', password='Password123')
        response = self.client.get(reverse('view_requests'))
        self.assertEqual(list(response.context['requests']), [])

    def test_post_request_is_bad_request(self):
        response = self.client.post(reverse('view_requests'))
        self.assertEqual(response.status_code, 405)

    def test_unauthenticated_user_cannot_view_request(self):
        self.client.logout()
        response = self.client.get(reverse('view_requests'))
        expected_url = f"{reverse('log_in')}?next={reverse('view_requests')}"
        self.assertRedirects(response, expected_url, status_code=302, target_status_code=200)