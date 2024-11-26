import os

from django.http import HttpResponse
from django.test import TestCase, override_settings
from django.conf import settings
from invoicer.models import get_latest_id_number
from user_system.models import User, KnowledgeArea, Day
from user_system.fixtures import create_test_users as create_fixtures
from invoicer.helpers.generate_invoice_id import generate_invoice_id
from request_handler.models import Request, Venue
from django.shortcuts import reverse

class TestGenerateInvoice(TestCase):

    def setUp(self):
        create_fixtures.create_test_user()
        self.student = User.objects.get(user_type='Student')
        self.tutor = User.objects.get(user_type='Tutor')
        self.admin = User.objects.get(user_type='Admin')
        self.original_setting_value = settings.USE_AWS_S3
        self.invoice_id = generate_invoice_id(self.student, get_latest_id_number(self.student))
        self.path = f'{settings.INVOICE_OUTPUT_PATH}/{self.invoice_id}.pdf'
        self.request = Request.objects.create(
            student=self.student,
            allocated=True,
            tutor=self.tutor,
            knowledge_area=KnowledgeArea.objects.filter(user=self.tutor).first().subject,
            frequency='Biweekly',
            duration='1h',
            venue=Venue.objects.get(venue='Online'),
            day=Day.objects.get(day='Monday'),
        )

    def test_generate_invoice_id(self):
        self.assertEqual(generate_invoice_id(self.student, get_latest_id_number(student=self.student)), str(self.invoice_id))

    @override_settings(USE_AWS_S3=False)
    def test_generate_invoice_local_store(self):
        self.assertions_for_local_invoice(self.generate_invoice())
        os.remove(self.path)

    @override_settings(USE_AWS_S3=False)
    def test_you_cannot_generate_invoices_if_they_already_exist(self):
        self.assertions_for_local_invoice(self.generate_invoice())
        self.client.force_login(self.admin)
        response = self.client.get(reverse('generate_invoice', kwargs={"request_id": self.request.id}))
        self.assertEqual(response.status_code, 204)
        os.remove(self.path)

    @override_settings(USE_AWS_S3=True)
    def test_generate_invoice(self):
        from code_tutors.aws import s3
        self.generate_invoice()
        key = f'invoices/pdfs/{self.invoice_id}.pdf'
        url = s3.generate_access_url(key=key)
        self.assertIsNotNone(url)
        self.assertTrue(isinstance(url, str))
        s3._delete(key)

    #----TEST HELPERS-----#
    def generate_invoice(self) -> HttpResponse:
        self.client.force_login(self.admin)
        return self.client.get(reverse("generate_invoice", kwargs={"request_id": self.request.id}))

    def assertions_for_local_invoice(self, response: HttpResponse) -> None:
        with open(self.path, 'rb') as file:
            self.assertIsNotNone(file)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.content, b"Invoice generated successfully!")
