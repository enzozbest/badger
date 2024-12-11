import os

from django.conf import settings
from django.shortcuts import reverse
from django.test import TestCase, override_settings

from invoicer.helpers.generate_invoice_id import generate_invoice_id
from invoicer.models import Invoice, get_latest_id_number
from request_handler.fixtures.create_test_requests import create_test_requests
from request_handler.models import Request
from user_system.fixtures.create_test_users import create_test_users
from user_system.models.user_model import User


class TestViewInvoices(TestCase):
    def setUp(self):
        create_test_users()
        create_test_requests()
        self.student = User.objects.get(user_type='Student')
        self.request_alloc = Request.objects.get(allocated=True)
        self.invoice_id = generate_invoice_id(self.student, get_latest_id_number(self.student))
        self.path = f'{settings.INVOICE_OUTPUT_PATH}/{self.invoice_id}.pdf'

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)
        super().tearDown()

    @override_settings(USE_AWS_S3=False)
    def test_student_can_view_their_invoices_local(self):
        # Test invoice is retrieved correctly.
        self.generate_invoice()
        self.client.login(username='@charlie', password='Password123')
        response = self.client.get(f'{reverse("get_invoice", kwargs={"invoice_id": self.invoice_id})}', follow=True)
        self.assert_correct_retrieval(response)

    @override_settings(USE_AWS_S3=False)
    def test_tutors_cannot_view_invoices(self):
        self.generate_invoice()
        self.client.login(username='@janedoe', password='Password123')
        response = self.client.get(f'{reverse("get_invoice", kwargs={"invoice_id": self.invoice_id})}')
        self.assertEqual(response.status_code, 403)

    @override_settings(USE_AWS_S3=False)
    def test_admins_can_see_invoices(self):
        self.generate_invoice()
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(f'{reverse("get_invoice", kwargs={"invoice_id": self.invoice_id})}', follow=True)
        self.assert_correct_retrieval(response)

    @override_settings(USE_AWS_S3=False)
    def test_students_cannot_view_other_students_invoices(self):
        self.generate_invoice()
        user = User.objects.create(username='other', email='other@other.com', password='Password123',
                                   user_type='Student')
        self.client.force_login(user)
        response = self.client.get(f'{reverse("get_invoice", kwargs={"invoice_id": self.invoice_id})}')
        self.assertEqual(response.status_code, 403)

    @override_settings(USE_AWS_S3=False)
    def test_saving_existing_invoice_id_does_not_change_it(self):
        self.generate_invoice()
        invoice = Invoice.objects.get(invoice_id=self.invoice_id)
        invoice.save()
        self.assertEqual(invoice.invoice_id, self.invoice_id)

    @override_settings(USE_AWS_S3=False)
    def test_creating_new_invoice_stores_correct_id(self):
        invoice = Invoice.objects.create(student=self.student,
                                         total=0.0)
        self.assertEqual(invoice.invoice_id, self.invoice_id)

    def assert_correct_retrieval(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertIn('Content-Disposition', response.headers)
        self.assertEqual(response.headers['Content-Disposition'], f'attachment; filename="{self.invoice_id}.pdf"')
        self.assertIn('Content-Type', response.headers)
        self.assertEqual(response.headers['Content-Type'], 'application/pdf')

    @override_settings(USE_AWS_S3=False)
    def generate_invoice(self):
        self.client.login(username='@johndoe', password='Password123')
        self.client.get(f'{reverse("generate_invoice", kwargs={"tutoring_request_id": self.request_alloc.id})}')
        self.client.logout()
