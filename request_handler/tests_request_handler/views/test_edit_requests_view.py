from django.test import TestCase
from django.urls import reverse

from request_handler.forms import RequestForm
from request_handler.models.request_model import Request
from request_handler.models.venue_model import Venue
from request_handler.views.edit_request import create_recurring_requests, create_request
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
            knowledge_area='Robotics',
            term='September',
            frequency='Weekly',
            duration='1.5',
            is_recurring=False
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

    def test_making_a_request_recurring_creates_necessary_requests(self):
        self.client.force_login(self.student)
        data = {
            'knowledge_area': 'Robotics',
            'term': 'September',
            'frequency': 'Weekly',
            'duration': '1.5',
            'venue_preference': [self.mode_preference.pk],
            'is_recurring': True,
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(response, reverse('view_requests'), status_code=302, target_status_code=200)
        group = Request.objects.filter(group_request_id=self.request_instance.group_request_id)
        self.assertTrue(group.exists())
        self.assertEqual(group.count(), 3)

    def test_recurring_requests_disable_term_field(self):
        self.client.force_login(self.student)
        self.request_instance.is_recurring = True
        self.request_instance.save()
        response = self.client.get(self.url)
        self.assertNotIn('term', response.context)
        self.assertEqual(response.status_code, 200)

    def test_raises_exception_when_invalid_parameter(self):
        with self.assertRaises(ValueError):
            create_recurring_requests('INVALID_TERM',
                                      {'term': None, 'student': self.student, 'knowledge_area': 'Robotics',
                                       'frequency': 'Weekly', 'duration': '1.5',
                                       'group_request_id': self.request_instance.group_request_id,
                                       'is_recurring': True,
                                       'venue_preference': Venue.objects})

    def test_term_none_generates_all_recurring_requests(self):
        create_recurring_requests(None,
                                  {'term': None, 'student': self.student, 'knowledge_area': 'Robotics',
                                   'frequency': 'Weekly', 'duration': '1.5',
                                   'group_request_id': self.request_instance.group_request_id,
                                   'is_recurring': True,
                                   'venue_preference': Venue.objects})
        self.assertEqual(Request.objects.count(), 4)

    def test_create_request_without_venue_preference(self):
        create_request({'term': 'September', 'student': self.student, 'knowledge_area': 'Robotics',
                        'frequency': 'Weekly', 'duration': '1.5',
                        'group_request_id': self.request_instance.group_request_id,
                        'is_recurring': True, 'venue_preference': None})
        self.assertEqual(Request.objects.count(), 2)
        self.assertEqual(
            Request.objects.filter(student=self.student).filter(is_recurring=True).first().venue_preference.count(), 0)

    def test_edit_recurring_request_edits_all(self):
        create_recurring_requests(None, {'term': None, 'student': self.student, 'knowledge_area': 'Robotics',
                                         'frequency': 'Weekly', 'duration': '1.5',
                                         'group_request_id': self.request_instance.group_request_id,
                                         'is_recurring': True,
                                         'venue_preference': Venue.objects})
        self.assertEqual(Request.objects.count(), 4)
        req = Request.objects.filter(student=self.student).filter(is_recurring=True).first()
        self.client.force_login(self.admin)
        response = self.client.post(reverse('edit_request', kwargs={'pk': req.pk}), {
            'knowledge_area': 'Python', 'term': 'September',
            'frequency': 'Biweekly',
            'duration': '2',
            'venue_preference': [self.mode_preference.pk],
            'is_recurring': True,
        })
        group = Request.objects.exclude(id=req.id)
        self.assertTrue(group.exists())
        for request in group:
            self.assertTrue(request.is_recurring)
            self.assertEqual(request.knowledge_area, "Python")
            self.assertEqual(request.frequency, "Biweekly")
            self.assertEqual(request.duration, "2")

    def test_requests_cannot_be_made_recurring(self):
        self.request_instance.term = 'May'
        self.request_instance.save()
        self.request_instance.refresh_from_db()
        self.client.force_login(self.admin)
        response = self.client.post(self.url, {
            'knowledge_area': 'Python', 'term': 'September',
            'frequency': 'Biweekly',
            'duration': '2',
            'venue_preference': [self.mode_preference.pk],
            'is_recurring': True,
        })
        self.assertIn('You cannot make this request recurring!', str(response.context['form'].errors.get('term')))
        self.assertFalse(self.request_instance.is_recurring)

    def test_post_valid_edit_request(self):
        self.client.force_login(self.student)
        data = {
            'knowledge_area': 'Python',
            'term': 'September',
            'frequency': 'Biweekly',
            'duration': '2',
            'venue_preference': [self.mode_preference.pk],
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(response, reverse('view_requests'))

        self.request_instance.refresh_from_db()
        self.assertEqual(self.request_instance.knowledge_area, 'Python')
        self.assertEqual(self.request_instance.term, 'September')
        self.assertEqual(self.request_instance.frequency, 'Biweekly')
        self.assertEqual(self.request_instance.duration, '2')

    def test_post_missing_venue_preference(self):
        self.client.force_login(self.student)
        data = {
            'knowledge_area': 'Python',
            'term': 'September',
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
