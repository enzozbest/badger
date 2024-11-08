from django.test import TestCase
from django.urls import reverse
from tutorials.models import User
from request_handler.models import Request, Modality, Day

INVALID_REQUEST_ID = 999

class DeleteRequestViewTest(TestCase):

    def setUp(self):

        # Set up test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')

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


    # Test that the delete confirmation page loads for a valid request ID
    def test_get_delete_request(self):
        self.client.login(username='testuser', password='testpassword') # should be logged in
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
        self.client.login(username='testuser', password='testpassword')
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
        self.client.login(username='testuser', password='testpassword')
        invalid_url = reverse('delete_request', kwargs={'pk': INVALID_REQUEST_ID})
        before_count = Request.objects.count()
        response = self.client.post(invalid_url, follow=True)
        after_count = Request.objects.count()

        self.assertEqual(after_count, before_count)
        self.assertRedirects(response, reverse('view_requests'))


    # Tests that an unauthenticated user is redirected when attempting to delete a request
    def test_redirect_if_not_logged_in(self):
        self.client.logout()
        response = self.client.get(reverse('delete_request', args=[self.request_instance.id]))
        self.assertRedirects(response, f'/log_in/')
