import os

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import reverse
from django.test import TestCase, override_settings

from invoicer.helpers.generate_invoice_id import generate_invoice_id
from invoicer.models import get_latest_id_number
from request_handler.fixtures.create_test_requests import create_test_requests
from request_handler.models import Request
from user_system.fixtures.create_test_users import create_test_users
from user_system.models import User


class TestPaymentStatus(TestCase):
    def setUp(self):
        create_test_users()
        create_test_requests()
        self.admin = User.objects.get(user_type='Admin')
        self.request_alloc = Request.objects.get(allocated=True)
        self.invoice_id = generate_invoice_id(self.request_alloc.student,
                                              get_latest_id_number(self.request_alloc.student))
        self.path = f'{settings.INVOICE_OUTPUT_PATH}/{self.invoice_id}.pdf'

    @override_settings(USE_AWS_S3=False)
    def test_admin_can_set_as_paid_for_generated_invoice(self):
        self.invoice_assertions(self.generate_invoice())
        self.request_alloc.refresh_from_db()
        self.client.force_login(self.admin)
        response = self.client.post(reverse('set_payment_status', kwargs={'invoice_id': self.invoice_id,
                                                                          "payment_status": 1}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.request_alloc.invoice.payment_status, True)
        os.remove(self.path)

    @override_settings(USE_AWS_S3=False)
    def test_admin_can_set_as_unpaid_for_generated_invoice(self):
        self.invoice_assertions(self.generate_invoice())
        self.request_alloc.refresh_from_db()
        self.client.force_login(self.admin)
        response = self.client.post(reverse('set_payment_status', kwargs={'invoice_id': self.invoice_id,
                                                                          "payment_status": 0}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.request_alloc.invoice.payment_status, False)
        os.remove(self.path)

    @override_settings(USE_AWS_S3=False)
    def test_get_request_is_not_allowed(self):
        self.invoice_assertions(self.generate_invoice())
        self.request_alloc.refresh_from_db()
        self.client.force_login(self.admin)
        previous_status = self.request_alloc.invoice.payment_status
        response = self.client.get(reverse('set_payment_status', kwargs={'invoice_id': self.invoice_id,
                                                                         'payment_status': 1}))
        self.assertEqual(response.status_code, 405)
        new_status = self.request_alloc.invoice.payment_status
        self.assertEqual(previous_status, new_status)

    @override_settings(USE_AWS_S3=False)
    def test_non_admins_cannot_change_payment_status(self):
        self.invoice_assertions(self.generate_invoice())
        self.request_alloc.refresh_from_db()
        self.client.force_login(self.request_alloc.student)
        response = self.client.post(reverse('set_payment_status', kwargs={'invoice_id': self.invoice_id,
                                                                          "payment_status": 1}))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.content, b'You must be an admin to view this page')
        self.client.force_login(self.request_alloc.tutor)
        response = self.client.get(reverse('set_payment_status', kwargs={'invoice_id': self.invoice_id,
                                                                         "payment_status": 1}))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.content, b'You must be an admin to view this page')
        os.remove(self.path)

    @override_settings(USE_AWS_S3=False)
    def generate_invoice(self) -> HttpResponse:
        self.client.force_login(self.admin)
        return self.client.get(f'{reverse("generate_invoice", kwargs={"tutoring_request_id": self.request_alloc.id})}')

    @override_settings(USE_AWS_S3=False)
    def invoice_assertions(self, response: HttpResponse):
        with open(self.path, 'rb') as file:
            self.assertIsNotNone(file)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.content, b"Invoice generated successfully!")
