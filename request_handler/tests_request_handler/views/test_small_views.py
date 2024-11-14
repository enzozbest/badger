from django.test import TestCase
from django.shortcuts import reverse

class SmallViewsTestCase(TestCase):
    def setUp(self):
        pass

    def test_permission_denied_view(self):
        response = self.client.get(reverse('permission_denied'))
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'permission_denied.html')

    def test_request_success(self):
        response = self.client.get(reverse('request_success'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'request_success.html')