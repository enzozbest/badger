import os
from unittest import skipIf

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.shortcuts import reverse
from django.test import override_settings
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from code_tutors.test_selenium_functional_tests import log_in_via_form, logout, wait, wait_for_clickable, \
    wait_for_element
from invoicer.models import Invoice
from request_handler.fixtures.create_test_requests import create_test_requests
from request_handler.models.request_model import Request
from request_handler.models.venue_model import Venue
from user_system.fixtures.create_test_users import create_test_users
from user_system.models.user_model import User


@override_settings(USE_AWS_S3=False)
@skipIf(os.environ.get('GITHUB_ACTIONS') == 'true', 'These tests require headed browsers to work properly')
class TestFunctionalRegistration(StaticLiveServerTestCase):
    def setUp(self):
        create_test_users()
        self.student = User.objects.get(user_type=User.ACCOUNT_TYPE_STUDENT)
        self.tutor = User.objects.get(user_type=User.ACCOUNT_TYPE_TUTOR)
        self.admin = User.objects.get(user_type=User.ACCOUNT_TYPE_ADMIN)

        Venue.objects.create(venue="Online")
        Venue.objects.create(venue="In Person")
        Venue.objects.create(venue="No Preference")
        create_test_requests()
        self.allocated_request = Request.objects.get(allocated=True)
        self.unallocated_request = Request.objects.get(allocated=False)

        self.driver = webdriver.Firefox()
        self.driver.maximize_window()

    def tearDown(self):
        self.driver.quit()
        invoice = Invoice.objects.filter(student=self.student).first()
        if invoice:
            path = f'{settings.INVOICE_OUTPUT_PATH}/{invoice.invoice_id}.pdf'
            if os.path.exists(path):
                os.remove(path)

    def test_admin_can_see_invoice_generation_link_for_allocated_request(self):
        self.navigate_to_requests_page(self.admin)
        try:
            generate_invoice = wait_for_clickable(self.driver, wait_for_element(self.driver, By.ID,
                                                                                f"id_generate_invoice_{self.allocated_request.id}"))
            self.assertTrue(generate_invoice.is_displayed())
            self.assertTrue(generate_invoice.is_enabled())
        except NoSuchElementException:
            self.fail("Generate invoice button not found for allocated request")

    def test_admin_cannot_see_invoice_generation_link_for_unallocated_request(self):
        self.navigate_to_requests_page(self.admin)
        with self.assertRaises(NoSuchElementException):
            self.driver.find_element(By.ID, f"id_generate_invoice_{self.unallocated_request.id}")

    def test_tutors_cannot_see_invoice_generation_links(self):
        self.navigate_to_requests_page(self.tutor)
        with self.assertRaises(NoSuchElementException):
            self.driver.find_element(By.ID, f"id_generate_invoice_{self.unallocated_request.id}")
        with self.assertRaises(NoSuchElementException):
            self.driver.find_element(By.ID, f"id_generate_invoice_{self.unallocated_request.id}")

    def test_students_cannot_see_invoice_generation_links(self):
        self.navigate_to_requests_page(self.student)
        with self.assertRaises(NoSuchElementException):
            self.driver.find_element(By.ID, f"id_generate_invoice_{self.unallocated_request.id}")
        with self.assertRaises(NoSuchElementException):
            self.driver.find_element(By.ID, f"id_generate_invoice_{self.unallocated_request.id}")

    @override_settings(USE_AWS_S3=False)
    def test_admin_can_generate_an_invoice(self):
        self.navigate_to_requests_page(self.admin)
        generate_invoice = wait_for_clickable(self.driver, wait_for_element(self.driver, By.ID,
                                                                            f"id_generate_invoice_{self.allocated_request.id}"))
        generate_invoice.click()
        wait(self.driver)
        self.assertEqual(self.driver.current_url,
                         f"{self.live_server_url}{reverse('generate_invoice', kwargs={'tutoring_request_id': self.allocated_request.id})}")
        self.assertIn("Invoice generated successfully!".lower(), self.driver.page_source.lower())
        invoices = Invoice.objects.filter(student=self.student)
        self.assertTrue(invoices.exists())
        self.assertEqual(invoices.count(), 1)
        self.assertTrue(os.path.exists(f'{settings.INVOICE_OUTPUT_PATH}/{invoices.first().invoice_id}.pdf'))

    @override_settings(USE_AWS_S3=False)
    def test_students_cannot_generate_an_invoice(self):
        self.generate_invoice(self.student)
        self.assertEqual(self.driver.current_url,
                         f"{self.live_server_url}{reverse('generate_invoice', kwargs={'tutoring_request_id': self.allocated_request.id})}")
        self.assertIn("Permission Denied".lower(), self.driver.page_source.lower())
        invoices = Invoice.objects.filter(student=self.student)
        self.assertFalse(invoices.exists())
        self.assertEqual(invoices.count(), 0)
        self.assertFalse(os.path.exists(
            f'{settings.INVOICE_OUTPUT_PATH}/{invoices.first().invoice_id if invoices.first() else ""}.pdf'))

    @override_settings(USE_AWS_S3=False)
    def test_tutors_cannot_generate_an_invoice(self):
        self.generate_invoice(self.tutor)
        self.assertEqual(self.driver.current_url,
                         f"{self.live_server_url}{reverse('generate_invoice', kwargs={'tutoring_request_id': self.allocated_request.id})}")
        self.assertIn("Permission Denied".lower(), self.driver.page_source.lower())
        invoices = Invoice.objects.filter(student=self.student)
        self.assertFalse(invoices.exists())
        self.assertEqual(invoices.count(), 0)
        self.assertFalse(os.path.exists(
            f'{settings.INVOICE_OUTPUT_PATH}/{invoices.first().invoice_id if invoices.first() else ""}.pdf'))

    @override_settings(USE_AWS_S3=False)
    def test_invoice_already_generated(self):
        self.generate_invoice(self.admin)
        self.driver.refresh()
        self.assertIn("Invoice already generated for this request!".lower(), self.driver.page_source.title().lower())

    @override_settings(USE_AWS_S3=False)
    def test_student_can_see_view_invoice_link(self):
        self.generate_invoice(self.admin)
        logout(self.driver, self.live_server_url)
        self.navigate_to_requests_page(self.student)
        try:
            view_invoice = wait_for_clickable(self.driver, wait_for_element(self.driver, By.ID,
                                                                            f"id_view_invoice_{Invoice.objects.filter(student=self.student).first().invoice_id}"))
            self.assertTrue(view_invoice.is_displayed())
            self.assertTrue(view_invoice.is_enabled())
        except NoSuchElementException:
            self.fail("View invoice button was not found in the page!")

    @override_settings(USE_AWS_S3=False)
    def test_student_can_view_invoice(self):
        self.generate_invoice(self.admin)
        logout(self.driver, self.live_server_url)
        self.navigate_to_requests_page(self.student)
        try:
            view_invoice = wait_for_clickable(self.driver, wait_for_element(self.driver, By.ID,
                                                                            f"id_view_invoice_{Invoice.objects.filter(student=self.student).first().invoice_id}"))
            view_invoice.click()
            self.assertEqual(self.driver.current_url, f"{self.live_server_url}{reverse('view_requests')}")
            wait(self.driver)
        except NoSuchElementException:
            self.fail("View invoice button was not found in the page!")

    @override_settings(USE_AWS_S3=False)
    def test_admins_can_view_invoice(self):
        self.generate_invoice(self.admin)
        logout(self.driver, self.live_server_url)
        self.navigate_to_requests_page(self.admin)
        try:
            view_invoice = wait_for_clickable(self.driver, wait_for_element(self.driver, By.ID,
                                                                            f"id_view_invoice_{Invoice.objects.filter(student=self.student).first().invoice_id}"))
            view_invoice.click()
            wait(self.driver)
            self.assertEqual(self.driver.current_url, f"{self.live_server_url}{reverse('view_requests')}")

        except NoSuchElementException:
            self.fail("View invoice button was not found in the page!")

    @override_settings(USE_AWS_S3=False)
    def test_tutors_cannot_view_invoice(self):
        self.generate_invoice(self.admin)
        logout(self.driver, self.live_server_url)
        log_in_via_form(self.driver, self.live_server_url, self.tutor.username, 'Password123')
        self.driver.get(
            f"{self.live_server_url}{reverse('get_invoice', kwargs={'invoice_id': Invoice.objects.filter(student=self.student).first().invoice_id})}")
        wait(self.driver)
        self.assertIn("You cannot view invoices as a tutor".lower(), self.driver.page_source.lower())

    @override_settings(USE_AWS_S3=False)
    def test_admins_can_see_view_invoice_link(self):
        self.generate_invoice(self.admin)
        logout(self.driver, self.live_server_url)
        self.navigate_to_requests_page(self.admin)
        try:
            view_invoice = wait_for_clickable(self.driver, wait_for_element(self.driver, By.ID,
                                                                            f"id_view_invoice_{Invoice.objects.filter(student=self.student).first().invoice_id}"))
            self.assertTrue(view_invoice.is_displayed())
            self.assertTrue(view_invoice.is_enabled())
        except NoSuchElementException:
            self.fail("View invoice button was not found in the page!")

    @override_settings(USE_AWS_S3=False)
    def test_tutors_cannot_see_view_invoice_link(self):
        self.generate_invoice(self.admin)
        logout(self.driver, self.live_server_url)
        self.navigate_to_requests_page(self.tutor)
        with self.assertRaises(NoSuchElementException):
            self.driver.find_element(By.ID,
                                     f"id_view_invoice_{Invoice.objects.filter(student=self.student).first().invoice_id}")

    def navigate_to_requests_page(self, user: User):
        log_in_via_form(self.driver, self.live_server_url, user.username, 'Password123')
        self.driver.get(f"{self.live_server_url}{reverse('view_requests')}")
        wait(self.driver)

    @override_settings(USE_AWS_S3=False)
    def generate_invoice(self, user: User):
        log_in_via_form(self.driver, self.live_server_url, user.username, 'Password123')
        self.driver.get(
            f"{self.live_server_url}{reverse('generate_invoice', kwargs={'tutoring_request_id': self.allocated_request.id})}")
        wait(self.driver)
