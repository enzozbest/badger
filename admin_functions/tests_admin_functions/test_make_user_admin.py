from django.test import TestCase
from django.urls import reverse
from tutorials.models import User

class MakeUserAdminTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@test.com', password='Password123', user_type='Admin')
        for i in range(51):
            User.objects.create(username='@user{}'.format(i), password='Password123', email='user{}@test.com'.format(i),
                                user_type= 'Student' if i % 2 == 0 else 'Tutor')


    def test_invalid_post_request_make_user_admin(self):
        self.client.login(username='testuser', password='Password123')
        response = self.client.post(reverse('make_admin', args=[2]))
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.content, b'Method Not Allowed')

    def test_invalid_get_request_confirm_make_user_admin(self):
        self.client.login(username='testuser', password='Password123')
        response = self.client.get(reverse('confirm_make_admin', args=[2]))
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.content, b'Method Not Allowed')

    def test_unauthenticated_user_make_user_admin(self):
        response = self.client.get(reverse('make_admin', args=[2]), follow=True)
        self.assertRedirects(response, reverse('log_in'), status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'log_in.html')

    def test_unauthenticated_user_confirm_make_user_admin(self):
        response = self.client.post(reverse('confirm_make_admin', args=[2]), follow=True)
        self.assertRedirects(response, reverse('log_in'), status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'log_in.html')

    def test_nonadmin_user_make_user_admin(self):
        self.user = User.objects.create_user(username='testuser2', email='test2@test.com', password='Password123', user_type='Tutor')
        self.client.login(username='testuser2', password='Password123')
        response = self.client.get(reverse('make_admin', args=[2]), follow=True)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'permission_denied.html')

    def test_nonadmin_user_confirm_make_user_admin(self):
        self.user = User.objects.create_user(username='testuser2', email='test2@test.com', password='Password123', user_type='Tutor')
        self.client.login(username='testuser2', password='Password123')
        response = self.client.post(reverse('confirm_make_admin', args=[2]), follow=True)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'permission_denied.html')

    def test_make_user_admin(self):
        self.client.login(username='testuser', password='Password123')
        response = self.client.get(reverse('make_admin', args=[2]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'make_user_admin.html')

    def test_confirm_make_user_admin(self):
        self.client.login(username='testuser', password='Password123')
        response = self.client.post(reverse('confirm_make_admin', args=[2]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.get(pk=2).user_type,"Admin")
        self.assertTemplateUsed(response, 'confirm_make_user_admin.html')