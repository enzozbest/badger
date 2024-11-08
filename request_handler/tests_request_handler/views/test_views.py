from django.urls import reverse

from django.test import TestCase
from tutorials.models import User
from request_handler.models import Day, Modality

class TestViews(TestCase):
    def setUp(self):
        self.monday = Day.objects.create(day='Monday')
        self.online = Modality.objects.create(mode='Online')
        User.objects.create_user(username='@johndoe', email='johndoe@example.org', password='Password123')
        self.url = reverse('create_request')

    def test_unauthenticated_user_cannot_create_request(self):
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, reverse('log_in'), status_code=302, target_status_code=200)

    def test_user_can_see_rqeuest_creation_page(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_create_request_with_valid_data(self):
        self.client.login(username='@johndoe', password='Password123')
        data = {
            'available_days': [self.monday.pk],
            'term': 'Easter',
            'knowledge_area': 'Scala',
            'frequency': 'Weekly',
            'duration': '1h',
            'mode_preference': [self.online.pk],
        }
        response = self.client.post(self.url, data, follow=True)
        self.assertRedirects(response, reverse('request_success'), status_code=302, target_status_code=200)

    def test_create_request_with_invalid_data(self):
        self.client.login(username='@johndoe', password='Password123')
        #Blank 'term' field!
        data = {
            'available_days': [self.monday.id,],
            'term': '',
            'knowledge_area': 'Scala',
            'frequency': 'Weekly',
            'duration': '1h',
            'mode_preference': [self.online.id,]
        }
        self.client.post(self.url, data)
        self.assertRaises(ValueError)