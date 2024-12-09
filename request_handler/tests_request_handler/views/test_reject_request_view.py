from django.test import TestCase, Client
from django.urls import reverse
from user_system.models import User
from request_handler.models import Request
from request_handler.forms import RejectRequestForm
from django.http import HttpResponseForbidden

class RejectRequestViewTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(username='@admin', password='Password123', email="admin@example.com", user_type='Admin')
        self.regular_user = User.objects.create_user(username='@student', password='Password123', email="student@example.com", user_type='Student')
        self.request = Request.objects.create(student=self.regular_user, knowledge_area='Scala', term='2024', is_recurring=False, late=False)
        self.reject_url = reverse('reject_request', args=[self.request.id])

    #Test that non-admin users cannot access the reject request view.
    def test_reject_request_for_non_admin_user(self):
        self.client.login(username='@student', password='Password123')
        response = self.client.get(self.reject_url)
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    # Test that GET request loads the rejection form.
    def test_reject_request_get_method(self):
        self.client.login(username='@admin', password='Password123')
        response = self.client.get(self.reject_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Reason for rejection:')
        self.assertIsInstance(response.context['form'], RejectRequestForm)

    # Test that POST request with valid data rejects the request and saves the reason.
    def test_reject_request_post_valid(self):
        self.client.login(username='@admin', password='Password123')
        data = {'reason': 'Request was invalid.'}
        response = self.client.post(self.reject_url, data)

        # Ensure the request was updated with rejection details
        self.request.refresh_from_db()
        self.assertTrue(self.request.rejected_request)
        self.assertEqual(self.request.rejection_reason, 'Request was invalid.')

        self.assertRedirects(response, reverse('view_requests'))

    # Test that POST request with invalid data does not reject the request.
    def test_reject_request_post_invalid(self):
        self.client.login(username='@admin', password='Password123')
        data = {'reason': ''}  # Invalid as the reason is empty
        response = self.client.post(self.reject_url, data)

        # Ensure the request was not updated
        self.request.refresh_from_db()
        self.assertFalse(self.request.rejected_request)
        self.assertEqual(self.request.rejection_reason, None)

        self.assertFormError(response, 'form', 'reason', 'This field is required.')

    # Test that trying to reject a non-existing request raises a 404 error.
    def test_get_request_not_found(self):
        self.client.login(username='@admin', password='Password123')
        response = self.client.get(reverse('reject_request', args=[9999]))  # Non-existing ID
        self.assertEqual(response.status_code, 404)

    # Test that after rejection, the user is redirected to view_requests.
    def test_redirect_after_successful_rejection(self):
        self.client.login(username='@admin', password='Password123')
        data = {'reason': 'Invalid request details.'}
        response = self.client.post(self.reject_url, data)
        self.assertRedirects(response, reverse('view_requests'))
