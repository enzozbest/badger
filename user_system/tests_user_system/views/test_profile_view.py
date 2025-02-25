from decimal import Decimal

from django.contrib import messages
from django.test import TestCase
from django.urls import reverse

from user_system.fixtures.create_test_users import create_test_users
from user_system.forms.user_form import UserForm
from user_system.models.user_model import User
from user_system.tests_user_system.helpers import reverse_with_next


class ProfileViewTest(TestCase):
    """Test suite for the profile view."""

    def setUp(self):
        create_test_users()
        self.user = User.objects.get(username='@johndoe')
        self.url = reverse('profile')
        self.form_input = {
            'first_name': 'John2',
            'last_name': 'Doe2',
            'username': '@johndoe2',
            'email': 'johndoe2@example.org',
        }
        self.tutor_user = User.objects.get(username='@janedoe')
        self.student_user = User.objects.get(username='@charlie')
        self.client.force_login(self.user)

    def test_profile_url(self):
        self.assertEqual(self.url, '/profile/')

    def test_get_profile(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserForm))
        self.assertEqual(form.instance, self.user)

    def test_get_profile_redirects_when_not_logged_in(self):
        self.client.logout()
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_unsuccessful_profile_update(self):
        self.form_input['username'] = 'BAD_USERNAME'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserForm))
        self.assertTrue(form.is_bound)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, '@johndoe')
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.email, 'johndoe@example.org')

    def test_unsuccessful_profile_update_due_to_duplicate_username(self):
        self.form_input['username'] = '@janedoe'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserForm))
        self.assertTrue(form.is_bound)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, '@johndoe')
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.email, 'johndoe@example.org')

    def test_successful_profile_update(self):
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('dashboard')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'dashboard.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, '@johndoe2')
        self.assertEqual(self.user.first_name, 'John2')
        self.assertEqual(self.user.last_name, 'Doe2')
        self.assertEqual(self.user.email, 'johndoe2@example.org')

    def test_post_profile_redirects_when_not_logged_in(self):
        self.client.logout()
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, self.form_input)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_tutor_can_update_hourly_rate(self):
        self.client.logout()
        self.client.force_login(self.tutor_user)
        response = self.client.post(reverse('profile'), {
            'first_name': self.tutor_user.first_name,
            'last_name': self.tutor_user.last_name,
            'username': self.tutor_user.username,
            'email': self.tutor_user.email,
            'user_type': self.tutor_user.user_type,
            'hourly_rate': 20.00,  # Update hourly rate
        })
        self.assertEqual(response.status_code, 302)
        self.tutor_user.refresh_from_db()
        self.assertEqual(self.tutor_user.hourly_rate, Decimal('20.00'))

    def test_student_cannot_update_hourly_rate(self):
        self.client.force_login(self.student_user)
        response = self.client.post(reverse('profile'), {
            'first_name': self.student_user.first_name,
            'last_name': self.student_user.last_name,
            'username': self.student_user.username,
            'email': self.student_user.email,
            'user_type': self.student_user.user_type,
        })
        self.assertEqual(response.status_code, 302)
        self.student_user.refresh_from_db()
        self.assertIsNone(self.student_user.hourly_rate)  # Default hourly rate applies
