from django.test import TestCase
from request_handler.fixtures.create_test_requests import create_test_requests
from request_handler.models import Request, Venue
from user_system.fixtures.create_test_users import create_test_user
from django.shortcuts import reverse
from user_system.models import User, Day


class TestAllocation(TestCase):
    def setUp(self):
        create_test_user()
        create_test_requests()
        self.admin = User.objects.get(user_type=User.ACCOUNT_TYPE_ADMIN)
        self.tutor = User.objects.get(user_type=User.ACCOUNT_TYPE_TUTOR)
        self.student = User.objects.get(user_type=User.ACCOUNT_TYPE_STUDENT)
        self.allocated_request = Request.objects.get(allocated=True)
        self.unallocated_request = Request.objects.get(allocated=False)
        self.online = Venue.objects.get(venue='Online')
        self.tuesday = Day.objects.get(day='Tuesday')


    def test_allocated_request_exists(self):
        self.assertIsNotNone(self.allocated_request)

    def test_unallocated_request_exists(self):
        self.assertIsNotNone(self.unallocated_request)

    def test_unauthenticated_user_cannot_see_page(self):
        response = self.client.get(reverse('allocate_request', args={self.unallocated_request.id}))
        self.assertRedirects(response, f'{reverse("log_in")}?next={reverse("allocate_request", args={self.unallocated_request.id})}', status_code=302, target_status_code=200)

    def test_student_cannot_allocate_requests_get(self):
        self.client.login(username=self.student.username, password='Password123')
        response = self.client.get(reverse("allocate_request", args={self.unallocated_request.id}))
        self.assertEqual(response.status_code, 401)
        self.assertTemplateUsed("permission_denied.html")

    def test_student_cannot_allocate_requests_post(self):
        self.client.login(username=self.student.username, password='Password123')
        response = self.client.post(reverse("allocate_request", args={self.unallocated_request.id}))
        self.assertEqual(response.status_code, 401)
        self.assertTemplateUsed("permission_denied.html")

    def test_tutors_cannot_allocate_requests_get(self):
        self.client.login(username=self.tutor.username, password='Password123')
        response = self.client.get(reverse("allocate_request", args={self.unallocated_request.id}))
        self.assertEqual(response.status_code, 401)
        self.assertTemplateUsed("permission_denied.html")

    def test_tutors_cannot_allocate_requests_post(self):
        self.client.login(username=self.tutor.username, password='Password123')
        response = self.client.post(reverse("allocate_request", args={self.unallocated_request.id}))
        self.assertEqual(response.status_code, 401)
        self.assertTemplateUsed("permission_denied.html")

    def admin_can_send_get_request(self):
        self.client.login(username=self.admin.username, password='Password123')
        response = self.client.get(reverse("allocate_request", args={self.unallocated_request.id}))
        self.assertEqual(response.status_code, 200)

    def admin_can_send_post_request(self):
        self.client.login(username=self.admin.username, password='Password123')
        response = self.client.post(reverse("allocate_request", args={self.unallocated_request.id}))
        self.assertEqual(response.status_code, 200)

    def test_attempting_to_allocate_allocated_request_fails(self):
        self.client.login(username=self.admin.username, password='Password123')
        response = self.client.get(reverse("allocate_request", args={self.allocated_request.id}))
        self.assertEqual(response.status_code, 409)
        self.assertTemplateUsed("already_allocated_error.html")

    def test_allocating_allocated_request_fails(self):
        self.client.login(username=self.admin.username, password='Password123')
        response = self.client.post(reverse("allocate_request", args={self.allocated_request.id}))
        self.assertEqual(response.status_code, 409)
        self.assertTemplateUsed("already_allocated_error.html")

    def test_allocating_unallocated_request_works(self):
        self.client.login(username=self.admin.username, password='Password123')
        response = self.client.post(reverse("allocate_request", args={self.unallocated_request.id}), data={
            'tutor': self.tutor.id,
            'venue': str(self.online.id),
            'day': self.tuesday.id
        })
        self.unallocated_request.refresh_from_db()
        self.assertRedirects(response, reverse('view_requests'), status_code=302, target_status_code=200)
        self.assertTrue(self.unallocated_request.allocated)
        self.assertIsNotNone(self.unallocated_request.tutor)
        self.assertIsNotNone(self.unallocated_request.venue)
        self.assertIsNotNone(self.unallocated_request.day)

    def test_invalid_allocation_reloads_form(self):
        self.client.login(username=self.admin.username, password='Password123')
        response = self.client.post(reverse("allocate_request", args={self.unallocated_request.id}), data={
           'tutor': 'AAAAAAAAAAA'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("allocate_request.html")

    def test_get_method_unallocated_request(self):
        self.client.login(username=self.admin.username, password='Password123')
        response = self.client.get(reverse("allocate_request", args={self.unallocated_request.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("allocate_request.html")