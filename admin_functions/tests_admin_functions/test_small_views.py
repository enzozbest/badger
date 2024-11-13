from django.test import TestCase
from tutorials.models import User
from django.shortcuts import reverse
class SmallViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@test.com', password='Password123', user_type='Admin')

    def test_unauthenticated_user_cannot_access_admin_dashboard(self):
        response = self.client.get(reverse('admin_dash'), follow=True)
        self.assertRedirects(response, reverse('log_in'), status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'log_in.html')

    def test_admin_dashboard_not_accesible_via_post(self):
        self.client.login(username='testuser', password='Password123')
        response = self.client.post(reverse('admin_dash'))
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.content, b'Not Allowed')

    def test_student_cannot_access_admin_dashboard(self):
        student = User.objects.create_user(username='testuser2', email='test2@test.com', password='Password123', user_type='Student')
        self.client.login(username='testuser2', password='Password123')
        response = self.client.get(reverse('admin_dash'))
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'permission_denied.html')

    def test_tutor_cannot_access_admin_dashboard(self):
        tutor = User.objects.create_user(username='testuser2', email='test2@test.com', password='Password123',
                                           user_type='Tutor')
        self.client.login(username='testuser2', password='Password123')
        response = self.client.get(reverse('admin_dash'))
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'permission_denied.html')

    def test_admin_can_access_admin_dashboard(self):
        self.client.login(username='testuser', password='Password123')
        response = self.client.get(reverse('admin_dash'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_dashboard.html')
