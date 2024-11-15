from django.test import TestCase
from django.urls import reverse
from user_system.models import User
from request_handler.models import Request, Modality, Day
from django.contrib import messages
from unittest.mock import patch

INVALID_REQUEST_ID = 999999999

class DeleteRequestViewTest(TestCase):
    def setUp(self):

        # Set up test user
        self.user = User.objects.create_user(username='testuser', password='Password123', user_type='Student')

        self.mode_preference = Modality.objects.create(mode="Online")
        self.available_day = Day.objects.create(day="Monday")

        # Request instance belonging to test user
        self.request_instance = Request.objects.create(
            student=self.user,
            knowledge_area='C++',
            term='Easter',
            frequency='Weekly',
            duration='1h',
        )
        self.request_instance.availability.set([self.available_day])
        self.request_instance.venue_preference.set([self.mode_preference])

        self.url = reverse('delete_request', kwargs={'pk': self.request_instance.pk})


    # Test that the URL is correctly formatted
    def test_delete_request_url(self):
        self.assertEqual(self.url, f'/request/{self.request_instance.pk}/delete/')

    def test_get_bad_request(self):
        response = self.client.get(self.url, kwargs={'pk': self.request_instance.pk})
        self.assertEqual(response.status_code, 400)

    # Test that the delete confirmation page loads for a valid request ID
    def test_get_delete_request(self):
        self.client.login(username='testuser', password='Password123') # should be logged in
        # response = self.client.get(self.url)
        response = self.client.get(reverse('confirm_delete_request', kwargs={'pk': self.request_instance.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'confirm_delete_request.html')


    # Test GET request to delete non-existent request returns 404 error
    def test_get_delete_request_with_invalid_pk(self):
        response = self.client.get('delete_request', kwargs={'pk': INVALID_REQUEST_ID})
        self.assertEqual(response.status_code, 404)


    # Test POST request with valid ID deletes request and redirects
    def test_post_with_valid_pk(self):
        self.client.login(username='testuser', password='Password123')
        before_count = Request.objects.count()
        response = self.client.post(self.url)
        after_count = Request.objects.count()

        self.assertEqual(after_count, before_count - 1)

        expected_redirect_url = reverse('view_requests')
        self.assertRedirects(response, expected_redirect_url, status_code=302, target_status_code=200)

        request_pk = self.request_instance.pk
        try:
            Request.objects.get(pk=request_pk)
            self.fail("Request should have been deleted. ")
        except Request.DoesNotExist: # if request does not exist after deletion
            pass


    # Test POST request with invalid ID does not delete from / change the database
    def test_post_with_invalid_pk(self):
        self.client.login(username='testuser', password='Password123', user_type='Student')
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
        self.assertRedirects(response, f'/log_in/')

    def test_post_confirm_delete_request(self):
        self.client.login(username='testuser', password='Password123', user_type='Student')
        response = self.client.post(reverse('confirm_delete_request', kwargs={'pk': self.request_instance.pk}))
        self.assertRedirects(response, reverse('view_requests'))

    # Tests for handling the post except block
    def test_post_with_invalid_request_pk(self):
        self.client.login(username='testuser', password='Password123', user_type='Student')
        invalid_url = reverse('delete_request', kwargs={'pk': INVALID_REQUEST_ID})
        before_count = Request.objects.count()
        response = self.client.post(invalid_url)
        after_count = Request.objects.count()
        self.assertEqual(after_count, before_count) # Should be no change
        self.assertRedirects(response, reverse('view_requests'))

        # Check if correct error message is added to the error framework
        message_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(message_list), 1) # There should only be 1 message
        self.assertTrue(str(message_list[0]).startswith("There was an error deleting this request"))
