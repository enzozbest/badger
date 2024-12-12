import os
from unittest import skipIf

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.shortcuts import reverse
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from code_tutors.test_selenium_functional_tests import log_in_via_form, wait, wait_for_clickable, wait_for_element
from request_handler.fixtures.create_test_requests import create_test_requests
from request_handler.models.venue_model import Venue

Venue
from request_handler.models.request_model import Request
from user_system.fixtures.create_test_users import create_test_users
from user_system.models.user_model import User

from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

@skipIf(os.environ.get('GITHUB_ACTIONS') == 'true', 'These tests require headed browsers to work properly')
class TestFunctionalRequestHandler(StaticLiveServerTestCase):
    def setUp(self):
        # Create a temporary Firefox profile
        profile = FirefoxProfile()  # This creates a default profile you can customize if needed

        # Set up options and associate the profile
        options = Options()
        options.profile = profile

        # Set up the Firefox WebDriver with the profile
        service = Service(executable_path='/snap/bin/geckodriver')  # Replace with the actual path to geckodriver
        self.driver = webdriver.Firefox(service=service, options=options)
        self.driver.maximize_window()

        create_test_users()
        self.student = User.objects.get(user_type=User.ACCOUNT_TYPE_STUDENT)
        self.tutor = User.objects.get(user_type=User.ACCOUNT_TYPE_TUTOR)
        self.admin = User.objects.get(user_type=User.ACCOUNT_TYPE_ADMIN)

        Venue.objects.get_or_create(venue="In Person")
        Venue.objects.get_or_create(venue="Online")
        Venue.objects.get_or_create(venue="No Preference")

    def tearDown(self):
        self.driver.quit()

    def test_student_can_create_a_request(self):
        log_in_via_form(self.driver, self.live_server_url, self.student.username, 'Password123')
        self.create_request_via_form(self.student)

    def test_tutor_cannot_create_a_request(self):
        log_in_via_form(self.driver, self.live_server_url, self.tutor.username, 'Password123')
        url = f"{self.live_server_url}{reverse('create_request')}"
        self.driver.get(url)
        self.assertIn("Permission Denied", self.driver.page_source)

    def test_student_can_edit_a_request(self):
        log_in_via_form(self.driver, self.live_server_url, self.student.username, 'Password123')
        create_test_requests()
        request = Request.objects.filter(student=self.student).first()
        self.driver.get(f'{self.live_server_url}{reverse("edit_request", kwargs={"pk": request.id})}')
        wait(self.driver)

        new_knowledge_area = Select(wait_for_element(self.driver, By.ID, "id_knowledge_area"))
        new_knowledge_area.select_by_visible_text("Python")
        submit_button = wait_for_clickable(self.driver, wait_for_element(self.driver, By.ID, "id_submit_button"))
        submit_button.click()

        wait(self.driver)
        self.assertEqual(self.driver.current_url, f"{self.live_server_url}{reverse('view_requests')}")
        self.assertTrue(Request.objects.filter(id=request.id).exists())
        request.refresh_from_db()
        self.assertEqual(request.knowledge_area, 'Python')

    def test_tutor_cannot_edit_a_request(self):
        log_in_via_form(self.driver, self.live_server_url, self.tutor.username, 'Password123')
        create_test_requests()
        request = Request.objects.all().first()
        url = f"{self.live_server_url}{reverse('edit_request', kwargs={'pk': request.id})}"
        self.driver.get(url)
        self.assertIn("Permission Denied", self.driver.page_source)

    def test_student_can_delete_a_request(self):
        log_in_via_form(self.driver, self.live_server_url, self.student.username, 'Password123')
        create_test_requests()
        request = Request.objects.filter(student=self.student).first()
        self.driver.get(f"{self.live_server_url}{reverse('confirm_delete_request', kwargs={'pk': request.id})}")
        wait(self.driver)

        submit_button = wait_for_clickable(self.driver, wait_for_element(self.driver, By.ID, "id_submit_button"))
        submit_button.click()

        wait(self.driver)
        self.assertEqual(self.driver.current_url, f"{self.live_server_url}{reverse('view_requests')}")
        self.assertFalse(Request.objects.filter(id=request.id).exists())

    def test_tutor_cannot_delete_a_request(self):
        log_in_via_form(self.driver, self.live_server_url, self.tutor.username, 'Password123')
        create_test_requests()
        request = Request.objects.all().first()
        url = f"{self.live_server_url}{reverse('delete_request', kwargs={'pk': request.id})}"
        self.driver.get(url)
        self.assertIn("Permission Denied", self.driver.page_source)

    def test_admin_can_create_a_request(self):
        log_in_via_form(self.driver, self.live_server_url, self.admin.username, 'Password123')
        self.create_request_via_form(self.admin)

    def test_admin_can_edit_a_request(self):
        log_in_via_form(self.driver, self.live_server_url, self.admin.username, 'Password123')
        create_test_requests()
        request = Request.objects.all().first()
        self.driver.get(f'{self.live_server_url}{reverse("edit_request", kwargs={"pk": request.id})}')
        wait(self.driver)

        new_knowledge_area = Select(wait_for_element(self.driver, By.ID, "id_knowledge_area"))
        new_knowledge_area.select_by_visible_text("Python")
        submit_button = wait_for_clickable(self.driver, wait_for_element(self.driver, By.ID, "id_submit_button"))
        submit_button.click()

        wait(self.driver)
        self.assertEqual(self.driver.current_url, f"{self.live_server_url}{reverse('view_requests')}")
        self.assertTrue(Request.objects.filter(id=request.id).exists())
        request.refresh_from_db()
        self.assertEqual(request.knowledge_area, 'Python')

    def test_admin_can_delete_a_request(self):
        log_in_via_form(self.driver, self.live_server_url, self.admin.username, 'Password123')
        create_test_requests()
        request = Request.objects.all().first()
        self.driver.get(f"{self.live_server_url}{reverse('confirm_delete_request', kwargs={'pk': request.id})}")
        wait(self.driver)

        submit_button = wait_for_clickable(self.driver, wait_for_element(self.driver, By.ID, "id_submit_button"))
        submit_button.click()

        wait(self.driver)
        self.assertEqual(self.driver.current_url, f"{self.live_server_url}{reverse('view_requests')}")
        self.assertFalse(Request.objects.filter(id=request.id).exists())

    def test_tutor_view_the_accept_request_button(self):
        create_test_requests()
        allocated_request = Request.objects.get(allocated=True)
        self.navigate_to_requests_page(self.tutor)
        try:
            button = wait_for_clickable(self.driver, wait_for_element(self.driver, By.ID,
                                                                      f"id_accept_request_{allocated_request.id}"))
            self.assertTrue(button.is_displayed())
            self.assertTrue(button.is_enabled())
        except NoSuchElementException:
            self.fail("The button was not visible")

    def test_student_cannot_view_the_accept_request_button(self):
        create_test_requests()
        allocated_request = Request.objects.get(allocated=True)
        self.navigate_to_requests_page(self.student)
        with self.assertRaises(NoSuchElementException):
            self.driver.find_element(By.ID,
                                     f"id_accept_request_{allocated_request.id}")

    def test_admin_cannot_view_the_accept_request_button(self):
        create_test_requests()
        allocated_request = Request.objects.get(allocated=True)
        self.navigate_to_requests_page(self.admin)
        with self.assertRaises(NoSuchElementException):
            self.driver.find_element(By.ID,
                                     f"id_accept_request_{allocated_request.id}")

    def test_tutor_can_accept_a_request(self):
        create_test_requests()
        allocated_request = Request.objects.get(allocated=True)
        self.navigate_to_requests_page(self.tutor)
        button = wait_for_clickable(self.driver, wait_for_element(self.driver, By.ID,
                                                                  f"id_accept_request_{allocated_request.id}"))
        button.click()
        wait(self.driver)
        with self.assertRaises(NoSuchElementException):
            self.driver.find_element(By.ID,
                                     f"id_accept_request_{allocated_request.id}")

    def test_admins_can_see_refuse_request_button(self):
        create_test_requests()
        unallocated_request = Request.objects.get(allocated=False)
        self.navigate_to_requests_page(self.admin)
        try:
            button = wait_for_clickable(self.driver,
                                        wait_for_element(self.driver, By.ID, f"id_reject_{unallocated_request.id}"))
            self.assertTrue(button.is_displayed())
            self.assertTrue(button.is_enabled())
        except NoSuchElementException:
            self.fail("The button was not visible")

    def test_students_cannot_see_refuse_request_button(self):
        create_test_requests()
        unallocated_request = Request.objects.get(allocated=False)
        self.navigate_to_requests_page(self.student)
        with self.assertRaises(NoSuchElementException):
            self.driver.find_element(By.ID, f"id_reject_{unallocated_request.id}")

    def test_tutors_cannot_see_refuse_request_button(self):
        create_test_requests()
        unallocated_request = Request.objects.get(allocated=False)
        self.navigate_to_requests_page(self.tutor)
        with self.assertRaises(NoSuchElementException):
            self.driver.find_element(By.ID, f"id_reject_{unallocated_request.id}")

    def test_admins_can_refuse_requests(self):
        create_test_requests()
        unallocated_request = Request.objects.get(allocated=False)
        self.navigate_to_requests_page(self.admin)
        button = wait_for_clickable(self.driver,
                                    wait_for_element(self.driver, By.ID, f"id_reject_{unallocated_request.id}"))
        button.click()
        wait(self.driver)
        self.assertEqual(self.driver.current_url,
                         f"{self.live_server_url}{reverse('reject_request', kwargs={'request_id': unallocated_request.id})}")
        try:
            reason = wait_for_element(self.driver, By.ID, "id_reason")
            reason.send_keys("Reason")
            submit = wait_for_clickable(self.driver, wait_for_element(self.driver, By.ID, "id_reject_request"))
            submit.click()
            wait(self.driver)
            self.assertEqual(self.driver.current_url, f"{self.live_server_url}{reverse('view_requests')}")
            unallocated_request.refresh_from_db()
            self.assertTrue(unallocated_request.rejected_request)
            self.assertIsNotNone(unallocated_request.rejection_reason)
        except NoSuchElementException:
            self.fail("The button was not visible")

    def test_students_cannot_refuse_requests(self):
        create_test_requests()
        unallocated_request = Request.objects.get(allocated=False)
        log_in_via_form(self.driver, self.live_server_url, self.student.username, 'Password123')
        self.driver.get(
            f"{self.live_server_url}{reverse('reject_request', kwargs={'request_id': unallocated_request.id})}")
        wait(self.driver)
        self.assertIn("You do not have permission to reject this request".lower(), self.driver.page_source.lower())
        unallocated_request.refresh_from_db()
        self.assertFalse(unallocated_request.rejected_request)
        self.assertIsNone(unallocated_request.rejection_reason)

    def test_tutors_cannot_refuse_requests(self):
        create_test_requests()
        unallocated_request = Request.objects.get(allocated=False)
        log_in_via_form(self.driver, self.live_server_url, self.tutor.username, 'Password123')
        self.driver.get(
            f"{self.live_server_url}{reverse('reject_request', kwargs={'request_id': unallocated_request.id})}")
        wait(self.driver)
        self.assertIn("You do not have permission to reject this request".lower(), self.driver.page_source.lower())
        unallocated_request.refresh_from_db()
        self.assertFalse(unallocated_request.rejected_request)
        self.assertIsNone(unallocated_request.rejection_reason)

    def create_request_via_form(self, user: User):
        self.driver.get(f'{self.live_server_url}{reverse("create_request")}')
        wait(self.driver)
        self.populate_create_request_fields(self.get_create_request_fields())
        wait(self.driver)
        self.assertEqual(self.driver.current_url, f"{self.live_server_url}{reverse('request_success')}")
        self.assertTrue(Request.objects.filter(student=user).exists())

    def get_create_request_fields(self) -> tuple:
        knowledge_area_input = Select(wait_for_element(self.driver, By.ID, "id_knowledge_area"))
        term_input = Select(wait_for_element(self.driver, By.ID, "id_term"))
        frequency = Select(wait_for_element(self.driver, By.ID, "id_frequency"))
        duration = Select(wait_for_element(self.driver, By.ID, "id_duration"))
        venue_preference = wait_for_clickable(self.driver, wait_for_element(self.driver, By.XPATH,
                                                                            '//*[@id="id_venue_preference_0"]'))
        submit_button = wait_for_clickable(self.driver, wait_for_element(self.driver, By.ID, "id_submit_button"))

        return knowledge_area_input, term_input, frequency, duration, venue_preference, submit_button

    def populate_create_request_fields(self, fields: tuple):
        knowledge_area_input, term_input, frequency, duration, venue_preference, submit_button = fields
        knowledge_area_input.select_by_visible_text("Scala")
        term_input.select_by_visible_text("May - July")
        frequency.select_by_visible_text("Weekly")
        duration.select_by_visible_text("1 hour")
        venue_preference.click()
        submit_button.click()

    def navigate_to_requests_page(self, user: User):
        log_in_via_form(self.driver, self.live_server_url, user.username, 'Password123')
        self.driver.get(f"{self.live_server_url}{reverse('view_requests')}")
        wait(self.driver)
