from django.contrib import messages
from django.test import TestCase
from django.urls import reverse

from request_handler.models.venue_model import Venue

Venue
from request_handler.models.request_model import Request
from user_system.fixtures.create_test_users import create_test_users
from user_system.models.user_model import User

INVALID_REQUEST_ID = 999999999


class DeleteRequestViewTest(TestCase):
    def setUp(self):
        create_test_users()
        self.student = User.objects.get(user_type="Student")
        self.tutor = User.objects.get(user_type="Tutor")
        self.admin = User.objects.get(user_type="Admin")

        self.mode_preference = Venue.objects.create(venue="Online")
        self.request_instance = Request.objects.create(
            student=self.student,
            knowledge_area='C++',
            term='Easter',
            frequency='Weekly',
            duration='1h',
        )
        self.request_instance.venue_preference.set([self.mode_preference])
        self.url = reverse('delete_request', kwargs={'pk': self.request_instance.pk})

    def test_delete_request_url(self):
        self.assertEqual(self.url, f'/requests/delete/{self.request_instance.pk}/')

    def test_get_bad_request(self):
        self.client.force_login(self.student)
        response = self.client.get(self.url, kwargs={'pk': self.request_instance.pk})
        self.assertEqual(response.status_code, 405)

    def test_tutors_cannot_delete_requests(self):
        self.client.force_login(self.tutor)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_users_cannot_confirm_delete_requests(self):
        self.client.logout()
        confirm_url = reverse('confirm_delete_request', kwargs={'pk': self.request_instance.pk})
        response = self.client.get(confirm_url)
        self.assertRedirects(response, f'{reverse("log_in")}?next={confirm_url}', status_code=302,
                             target_status_code=200)

    def test_tutors_cannot_confirm_delete_requests_get(self):
        self.client.force_login(self.tutor)
        response = self.client.get(reverse('confirm_delete_request', kwargs={'pk': self.request_instance.pk}))
        self.assertEqual(response.status_code, 403)

    def test_tutors_cannot_confirm_delete_requests_post(self):
        self.client.force_login(self.tutor)
        response = self.client.post(reverse('confirm_delete_request', kwargs={'pk': self.request_instance.pk}))
        self.assertEqual(response.status_code, 403)

    def test_other_student_cannot_confirm_delete_requests_get(self):
        other = self.create_other_student()
        self.client.force_login(other)
        response = self.client.get(reverse('confirm_delete_request', kwargs={'pk': self.request_instance.pk}))
        self.assertEqual(response.status_code, 403)

    def test_other_student_cannot_confirm_delete_requests_post(self):
        other = self.create_other_student()
        self.client.force_login(other)
        response = self.client.post(reverse('confirm_delete_request', kwargs={'pk': self.request_instance.pk}))
        self.assertEqual(response.status_code, 403)

    def test_other_student_cannot_delete_requests(self):
        other = self.create_other_student()
        self.client.force_login(other)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

    def test_get_delete_request(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse('confirm_delete_request', kwargs={'pk': self.request_instance.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'confirm_delete_request.html')

    def test_get_delete_request_with_invalid_pk(self):
        response = self.client.get('delete_request', kwargs={'pk': INVALID_REQUEST_ID})
        self.assertEqual(response.status_code, 404)

    def test_post_with_valid_pk(self):
        self.client.force_login(self.student)
        before_count = Request.objects.count()
        response = self.client.post(self.url)
        after_count = Request.objects.count()

        self.assertEqual(after_count, before_count - 1)

        expected_redirect_url = reverse('view_requests')
        self.assertRedirects(response, expected_redirect_url, status_code=302, target_status_code=200)

        request_pk = self.request_instance.pk
        try:
            Request.objects.get(pk=request_pk)
            self.fail("Request should have been deleted.")
        except Request.DoesNotExist:  # if request does not exist after deletion
            pass

    def test_post_with_invalid_pk(self):
        self.client.force_login(self.student)
        invalid_url = reverse('delete_request', kwargs={'pk': INVALID_REQUEST_ID})
        before_count = Request.objects.count()
        response = self.client.post(invalid_url, follow=True)
        after_count = Request.objects.count()

        self.assertEqual(after_count, before_count)
        self.assertRedirects(response, reverse('view_requests'))

    # Tests that an unauthenticated user is redirected when attempting to delete a request
    def test_redirect_if_not_logged_in(self):
        self.client.logout()
        response = self.client.post(reverse('delete_request', args=[self.request_instance.id]))
        expected_url = f'{reverse("log_in")}?next={self.url}'
        self.assertRedirects(response, expected_url, status_code=302, target_status_code=200)

    def test_post_confirm_delete_request(self):
        self.client.force_login(self.student)
        response = self.client.post(reverse('confirm_delete_request', kwargs={'pk': self.request_instance.pk}))
        self.assertRedirects(response, reverse('view_requests'))

    def test_post_with_invalid_request_pk(self):
        self.client.force_login(self.student)
        invalid_url = reverse('delete_request', kwargs={'pk': INVALID_REQUEST_ID})
        before_count = Request.objects.count()
        response = self.client.post(invalid_url)
        after_count = Request.objects.count()
        self.assertEqual(after_count, before_count)  # Should be no change
        self.assertRedirects(response, reverse('view_requests'))

        message_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(message_list), 1)  # There should only be 1 message
        self.assertTrue(str(message_list[0]).startswith("There was an error deleting this request"))

    def create_other_student(self) -> User:
        return User.objects.create_user(username='@other', password='Password123', user_type='Student')
