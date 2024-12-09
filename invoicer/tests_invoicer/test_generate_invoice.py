import os

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import reverse
from django.test import TestCase, override_settings

from invoicer.helpers.generate_invoice_id import generate_invoice_id
from invoicer.models import get_latest_id_number
from request_handler.models import Request, Venue
from user_system.fixtures import create_test_users as create_fixtures
from user_system.models.day_model import Day
from user_system.models.knowledge_area_model import KnowledgeArea
from user_system.models.user_model import User


class TestGenerateInvoice(TestCase):

    def setUp(self):
        create_fixtures.create_test_users()
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

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)
        super().tearDown()

    def test_generate_invoice_id(self):
        self.assertEqual(generate_invoice_id(self.student, get_latest_id_number(student=self.student)),
                         str(self.invoice_id))

    @override_settings(USE_AWS_S3=False)
    def test_generate_invoice_local_store(self):
        self._assertions_for_local_invoice(generate_invoice(self.client, self.admin, self.request.id))

    @override_settings(USE_AWS_S3=False)
    def test_you_cannot_generate_invoices_if_they_already_exist(self):
        self._assertions_for_local_invoice(generate_invoice(self.client, self.admin, self.request.id))
        self.client.force_login(self.admin)
        response = self.client.get(reverse('generate_invoice', kwargs={"tutoring_request_id": self.request.id}))
        self.assertEqual(response.status_code, 204)

    def _assertions_for_local_invoice(self, response: HttpResponse) -> None:
        with open(self.path, 'rb') as file:
            self.assertIsNotNone(file)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.content, b"Invoice generated successfully!")


def generate_invoice(client, admin, request_id) -> HttpResponse:
    client.force_login(admin)
    return client.get(reverse("generate_invoice", kwargs={"tutoring_request_id": request_id}))
