from django.test import TestCase
from django.urls import reverse
from user_system.models import User, Day
from request_handler.models import Request, Venue
from datetime import datetime 

INVALID_REQUEST_ID = 999

class TestViews(TestCase):
    def setUp(self):
        from user_system.fixtures.create_test_users import create_test_user
        create_test_user()
        self.monday, _ = Day.objects.get_or_create(day='Monday')
        self.online, _ = Venue.objects.get_or_create(venue='Online')
        self.student = User.objects.get(username='@charlie')
        self.tutor = User.objects.get(username='@janedoe')

        self.url = reverse('create_request')

    def test_user_can_see_rqeuest_creation_page(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_create_request_with_valid_data(self):
        self.client.login(username='@charlie', password='Password123')
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
        #Blank 'term' field!
        data = {
            'term': '',
            'knowledge_area': 'Scala',
            'frequency': 'Weekly',
            'duration': '1',
            'venue_preference': [self.online.id,]
        }
        self.client.post(self.url, data)
        self.assertRaises(ValueError)

    def test_tutor_cannot_create_request_get(self):
        self.client.login(username='@janedoe', password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 401)
        self.assertTemplateUsed(response, 'permission_denied.html')

    def test_tutor_cannot_create_request_post(self):
        self.client.login(username='@janedoe', password='Password123')
        response = self.client.post(self.url, follow=True)
        self.assertEqual(response.status_code, 401)
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
        #Purposefully choosing a late term
        if datetime.now().month >= 1 and datetime.now().month<5:
            data['term'] = 'January'
        elif datetime.now().month > 8 and datetime.now().month <= 12:
            data['term'] = 'September'
        elif datetime.now().month < 9 :
            data['term'] = 'May'

        url = reverse('create_request')
        response = self.client.post(url, data, follow=True)
        self.assertRedirects(response, reverse('processing_late_request'), status_code=302, target_status_code=200)

