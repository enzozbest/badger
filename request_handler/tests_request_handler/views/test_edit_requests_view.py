from django.test import TestCase
from django.urls import reverse
from user_system.models import User
from request_handler.models import Request, Venue, Day
from request_handler.forms import RequestForm

INVALID_REQUEST_ID = 999

class EditRequestViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='Password123', user_type='Student', email='testuser@example.com')
        self.tutor = User.objects.create_user(username='testtutor', password='Password123', user_type='Tutor', email='testtutor@example.com')
        self.admin = User.objects.create_user(username='adminuser', password='Password123', user_type='Admin', email='admin@example.com')
        self.mode_preference = Venue.objects.create(venue="Online")
        self.available_day = Day.objects.create(day="Monday")

        self.request_instance = Request.objects.create(
            student=self.user,
            knowledge_area='Ruby',
            term='May',
            frequency='Weekly',
            duration='1.5',
        )
        self.request_instance.availability.set([self.available_day])
        self.request_instance.venue_preference.set([self.mode_preference])

        self.url = reverse('edit_request', kwargs={'pk': self.request_instance.pk})

    def test_get_edit_request_view(self):
        self.client.login(username='testuser', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_request.html')
        self.assertIsInstance(response.context['form'], RequestForm)
        self.assertEqual(response.context['request_instance'], self.request_instance)


    def test_get_edit_request_with_invalid_pk(self):
        invalid_url = reverse('edit_request', kwargs={'pk': INVALID_REQUEST_ID})
        self.client.login(username='testuser', password='Password123')
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)


    def test_post_valid_edit_request(self):
        self.client.login(username='testuser', password='Password123')
        data = {
            'knowledge_area': 'Python',
            'term': 'May',
            'frequency': 'Biweekly',
            'duration': '2',
            'availability': [self.available_day.pk],
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
        self.client.login(username='testuser', password='Password123')
        data = {
            'knowledge_area': 'Python',
            'term': 'May',
            'frequency': 'Biweekly',
            'duration': '2',
            'availability': [self.available_day.pk],
            'venue_preference': [], 
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_request.html')
        self.assertContains(response, 'No venue preference set!')
