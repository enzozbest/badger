import os

from django.test import TestCase, override_settings
from django.conf import settings
from invoicer.models import Invoice, get_latest_id_number
from user_system.models import User, KnowledgeArea, Day
from user_system.fixtures import create_test_users as create_fixtures
from admin_functions.helpers import calculate_cost
from invoicer.helpers.generate_invoice_id import generate_invoice_id
from invoicer.helpers import invoice_generator
from request_handler.models import Request, Venue

class TestGenerateInvoice(TestCase):

    def setUp(self):
        create_fixtures.create_test_user()
        self.student = User.objects.get(user_type='Student')
        self.tutor = User.objects.get(user_type='Tutor')
        self.original_setting_value = settings.USE_AWS_S3
        settings.USE_AWS_S3 = False
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
        self.invoice = Invoice.objects.create(
            student=self.student,
            total=calculate_cost.calculate_cost(self.tutor, self.request.id)
        )
        self.request.invoice = self.invoice


    def test_generate_invoice_id(self):

        self.assertEqual(generate_invoice_id(self.student, get_latest_id_number(student=self.student)), str(self.invoice.invoice_id))

    @override_settings(USE_AWS_S3=False)
    def test_generate_invoice_local_store(self):
        invoice_generator.generate_invoice(self.request)
        path = f'{settings.INVOICE_OUTPUT_PATH}/{generate_invoice_id(self.student, get_latest_id_number(self.student))}.pdf'
        with open(path, 'rb') as file:
            self.assertIsNotNone(file)
        os.remove(path)

    @override_settings(USE_AWS_S3=True)
    def test_generate_invoice(self):
        from code_tutors.aws import s3
        invoice_generator.generate_invoice(self.request)
        path = f'invoices/pdfs/{generate_invoice_id(self.student, get_latest_id_number(self.student))}.pdf'
        url = s3.generate_access_url(key=path)
        self.assertIsNotNone(url)
        self.assertTrue(isinstance(url, str))
        s3._delete(path)
