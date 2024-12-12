from django.test import TestCase
from django.urls import reverse

from request_handler.forms import RequestForm
from request_handler.models.venue_model import Venue

Venue
from request_handler.models.request_model import Request
from user_system.fixtures.create_test_users import create_test_users
from user_system.models.user_model import User

INVALID_REQUEST_ID = 999


class EditRequestViewTest(TestCase):
    def setUp(self):
        create_test_users()
        self.student = User.objects.get(user_type='Student')
        self.tutor = User.objects.get(user_type='Tutor')
        self.admin = User.objects.get(user_type='Admin')

        self.mode_preference = Venue.objects.create(venue="Online")

        self.request_instance = Request.objects.create(
            student=self.student,
            knowledge_area='Ruby',
            term='May',
            frequency='Weekly',
            duration='1.5',
        )
        self.request_instance.venue_preference.set([self.mode_preference])
        self.request_instance.save()

        self.url = reverse('edit_request', kwargs={'pk': self.request_instance.pk})

    def test_unauthenticated_user_is_redirected_to_login(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f'{reverse("log_in")}?next={self.url}', status_code=302, target_status_code=200)

    def test_tutors_cannot_edit_request_get(self):
        self.client.force_login(self.tutor)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_tutors_cannot_edit_request_post(self):
        self.client.force_login(self.tutor)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

    def test_other_student_cannot_edit_request_get(self):
        other = self.create_other_student()
        self.client.force_login(other)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_get_edit_request_view(self):
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_request.html')
        self.assertIsInstance(response.context['form'], RequestForm)
        self.assertEqual(response.context['request_instance'], self.request_instance)

    def test_get_edit_request_with_invalid_pk(self):
        invalid_url = reverse('edit_request', kwargs={'pk': INVALID_REQUEST_ID})
        self.client.force_login(self.student)
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)

    def test_post_valid_edit_request(self):
        self.client.force_login(self.student)
        data = {
            'knowledge_area': 'Python',
            'term': 'May',
            'frequency': 'Biweekly',
            'duration': '2',
            'venue_preference': [self.mode_preference.pk],
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(response, reverse('view_requests'))

        self.request_instance.refresh_from_db()
        self.assertEqual(self.request_instance.knowledge_area, 'Python')
        self.assertEqual(self.request_instance.term, 'May')
        self.assertEqual(self.request_instance.frequency, 'Biweekly')
        self.assertEqual(self.request_instance.duration, '2')

    def test_post_missing_venue_preference(self):
        self.client.force_login(self.student)
        data = {
            'knowledge_area': 'Python',
            'term': 'May',
            'frequency': 'Biweekly',
            'duration': '2',
            'venue_preference': [],
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_request.html')
        self.assertContains(response, 'No venue preference set!')

    def create_other_student(self) -> User:
        return User.objects.create_user(username='@other', password='Password123', user_type='Student')
