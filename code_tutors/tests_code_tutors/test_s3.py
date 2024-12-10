from unittest import skipIf

from django.conf import settings
from django.shortcuts import reverse
from django.test import TestCase

from code_tutors.aws import s3
from invoicer.tests_invoicer.test_generate_invoice import generate_invoice, generate_invoice_id
from request_handler.fixtures.create_test_requests import create_test_requests
from request_handler.models import Request
from user_system.fixtures.create_test_users import create_test_users
from user_system.models.user_model import User


@skipIf(not settings.USE_AWS_S3, "These tests should only run if there is an appropriate local AWS configuration")
class TestS3(TestCase):
    def setUp(self):
        self.test_file_path = 'code_tutors/tests_code_tutors/resources/test.pdf'
        self.file_key = 'pdfs/test.pdf'

    def tearDown(self):
        s3._delete(self.file_key)

    def test_upload_file(self):
        with open(self.test_file_path, 'rb') as f:
            try:
                s3.upload(obj=f, key=self.file_key)
            except Exception as e:
                self.fail("Test raised an exception!")

    def test_get_access_url(self):
        with open(self.test_file_path, 'rb') as f:
            try:
                s3.upload(obj=f, key=self.file_key)
            except Exception as e:
                self.fail("Test raised an exception!")
        url = s3.generate_access_url(key=self.file_key)
        self.assertIsNotNone(url)
        self.assertTrue(isinstance(url, str))

    def test_generate_invoice(self):
        self.generate_invoice_in_s3()
        key = f'invoices/pdfs/{generate_invoice_id(User.objects.get(user_type="Student"), 0)}.pdf'
        url = s3.generate_access_url(key=key)
        self.assertIsNotNone(url)
        self.assertTrue(isinstance(url, str))
        s3._delete(key)

    def test_s3_URL_works(self):
        self.generate_invoice_in_s3()
        invoice_id = generate_invoice_id(User.objects.get(user_type="Student"), 0)
        response = self.client.get(reverse('get_invoice', kwargs={'invoice_id': invoice_id}))
        url = response.content.decode()
        self.assertRedirects(response, url, status_code=302, target_status_code=200, fetch_redirect_response=False)

    def generate_invoice_in_s3(self):
        create_test_users()
        create_test_requests()
        generate_invoice(self.client, User.objects.get(user_type='Admin'), Request.objects.get(allocated=True).id)
