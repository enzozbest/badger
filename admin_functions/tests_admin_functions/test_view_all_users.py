from django.test import TestCase
from django.urls import reverse
from tutorials.models import User


class ViewAllUsersTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@test.com', password='Password123', user_type='Admin')


    def test_post_request_not_allowed(self):
        self.client.login(username='testuser', password='Password123')
        response = self.client.post(reverse('view_all_users'))
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.content, b'Method Not Allowed')

    def test_unauthenticated_user_cannot_send_request(self):
        response = self.client.get(reverse('view_all_users'), follow=True)
        self.assertRedirects(response, reverse('log_in'), status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'log_in.html')

    def test_student_cannot_send_request(self):
        student = User.objects.create_user(username='testuser2', email='test2@test.com', password='Password123', user_type='Student')
        self.client.login(username='testuser2', password='Password123')
        response = self.client.get(reverse('view_all_users'))
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'permission_denied.html')

    def test_tutor_cannot_send_request(self):
        tutor = User.objects.create_user(username='testuser2', email='test2@test.com', password='Password123',
                                           user_type='Tutor')
        self.client.login(username='testuser2', password='Password123')
        response = self.client.get(reverse('view_all_users'))
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'permission_denied.html')

    def test_admin_can_send_request(self):
        self.client.login(username='testuser', password='Password123')
        response = self.client.get(reverse('view_all_users'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'view_users.html')

