from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.shortcuts import reverse
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select

from code_tutors.test_selenium_functional_tests import log_in_via_form, wait, wait_for_clickable, wait_for_element
from request_handler.fixtures.create_test_requests import create_test_requests
from request_handler.models import Request, Venue
from user_system.fixtures.create_test_users import create_test_users
from user_system.models.day_model import Day
from user_system.models.user_model import User


class TestFunctionalAdminFunctions(StaticLiveServerTestCase):
    def setUp(self):
        options = Options()
        options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=options)

        create_test_users()
        self.student = User.objects.get(user_type='Student')
        self.tutor = User.objects.get(user_type='Tutor')
        self.admin = User.objects.get(user_type='Admin')

        Venue.objects.get_or_create(venue="In Person")
        Venue.objects.get_or_create(venue="Online")
        Venue.objects.get_or_create(venue="No Preference")

        create_test_requests()

        self.unallocated_request = Request.objects.get(allocated=False)
        self.allocated_request = Request.objects.get(allocated=True)

    def tearDown(self):
        self.driver.quit()

    def test_admin_can_access_admin_dashboard(self):
        self.navigate_to_admin_dashboard(self.admin)
        self.assertEqual(self.driver.current_url, f"{self.live_server_url}{reverse('admin_dash')}")

    def test_student_cannot_access_admin_dashboard(self):
        self.navigate_to_admin_dashboard(self.student)
        self.assertIn("permission denied", self.driver.page_source.lower())

    def test_tutor_cannot_access_admin_dashboard(self):
        self.navigate_to_admin_dashboard(self.tutor)
        self.assertIn("permission denied", self.driver.page_source.lower())

    def test_admin_can_view_all_users(self):
        self.navigate_to_view_users_page(self.admin)
        self.assertEqual(self.driver.current_url, f"{self.live_server_url}{reverse('view_all_users')}")

    def test_student_cannot_view_all_users(self):
        self.navigate_to_view_users_page(self.student)
        self.assertIn("permission denied", self.driver.page_source.lower())

    def test_tutor_cannot_view_all_users(self):
        self.navigate_to_view_users_page(self.tutor)
        self.assertIn("permission denied", self.driver.page_source.lower())

    def test_admin_can_make_another_user_admin(self):
        self.navigate_to_view_users_page(self.admin)
        user_id = self.student.id
        make_admin = wait_for_clickable(self.driver, wait_for_element(self.driver, By.ID, f"id_make_admin_{user_id}"))
        make_admin.click()
        wait(self.driver)
        self.assertEqual(self.driver.current_url,
                         f"{self.live_server_url}{reverse('make_admin', kwargs={'pk': user_id})}")
        confirm = wait_for_clickable(self.driver, wait_for_element(self.driver, By.ID, f"id_confirm_admin_{user_id}"))
        confirm.click()
        wait(self.driver)
        self.assertEqual(self.driver.current_url,
                         f"{self.live_server_url}{reverse('confirm_make_admin', kwargs={'pk': user_id})}")

        self.student.refresh_from_db()
        self.assertEqual(self.student.user_type, 'Admin')

    def test_student_cannot_make_another_user_admin(self):
        log_in_via_form(self.driver, self.live_server_url, self.student.username, 'Password123')
        self.driver.get(f"{self.live_server_url}{reverse('make_admin', kwargs={'pk': self.tutor.id})}")
        self.assertIn("permission denied", self.driver.page_source.lower())
        self.student.refresh_from_db()
        self.assertNotEqual(self.student.user_type, 'Admin')

    def test_tutor_cannot_make_another_user_admin(self):
        log_in_via_form(self.driver, self.live_server_url, self.tutor.username, 'Password123')
        self.driver.get(f"{self.live_server_url}{reverse('make_admin', kwargs={'pk': self.student.id})}")
        self.assertIn("permission denied", self.driver.page_source.lower())
        self.student.refresh_from_db()
        self.assertNotEqual(self.student.user_type, 'Admin')

    def test_admin_can_click_request_allocation_button(self):
        self.navigate_to_requests_page_and_retrieve_allocate_button(self.admin)

    def test_student_cannot_click_request_allocation_button(self):
        self.navigate_to_view_requests_page(self.student)
        with self.assertRaises(NoSuchElementException):
            self.driver.find_element(By.ID, f"id_allocation_button_{self.unallocated_request.id}")

    def test_tutor_cannot_click_request_allocation_button(self):
        self.navigate_to_view_requests_page(self.tutor)
        with self.assertRaises(NoSuchElementException):
            self.driver.find_element(By.ID, f"id_allocation_button_{self.unallocated_request.id}")

    def test_admin_can_allocate_an_unallocated_request(self):
        button = self.navigate_to_requests_page_and_retrieve_allocate_button(self.admin)
        button.click()
        wait(self.driver)
        self.assertEqual(self.driver.current_url,
                         f"{self.live_server_url}{reverse('allocate_request', kwargs={'request_id': self.unallocated_request.id})}")
        day1 = Select(wait_for_element(self.driver, By.ID, f"id_day1"))
        day1.select_by_visible_text("Wednesday")
        wait(self.driver)

        venue = Select(wait_for_element(self.driver, By.ID, f"id_venue"))
        venue.select_by_visible_text("Online")
        wait(self.driver)

        tutor = Select(wait_for_element(self.driver, By.ID, f"id_tutor"))
        tutor.select_by_index(1)
        wait(self.driver)

        submit = wait_for_clickable(self.driver, wait_for_element(self.driver, By.ID, 'id_submit_request_allocation'))
        submit.click()
        wait(self.driver)

        self.assertEqual(self.driver.current_url, f"{self.live_server_url}{reverse('view_requests')}")
        self.unallocated_request.refresh_from_db()
        self.assertEqual(self.unallocated_request.allocated, True)
        self.assertEqual(self.unallocated_request.venue, Venue.objects.get(venue="Online"))
        self.assertEqual(self.unallocated_request.day, Day.objects.get(day="Wednesday"))
        self.assertEqual(self.unallocated_request.tutor, User.objects.get(user_type='Tutor'))

    def test_student_cannot_allocate_an_unallocated_request(self):
        log_in_via_form(self.driver, self.live_server_url, self.student.username, 'Password123')
        self.driver.get(
            f"{self.live_server_url}{reverse('allocate_request', kwargs={'request_id': self.unallocated_request.id})}")
        self.assertIn("permission denied", self.driver.page_source.lower())
        self.unallocated_request.refresh_from_db()
        self.assertEqual(self.unallocated_request.allocated, False)
        self.assertIsNone(self.unallocated_request.venue)
        self.assertIsNone(self.unallocated_request.day)
        self.assertIsNone(self.unallocated_request.tutor)

    def test_tutor_cannot_allocate_an_unallocated_request(self):
        log_in_via_form(self.driver, self.live_server_url, self.tutor.username, 'Password123')
        self.driver.get(
            f"{self.live_server_url}{reverse('allocate_request', kwargs={'request_id': self.unallocated_request.id})}")
        self.assertIn("permission denied", self.driver.page_source.lower())
        self.unallocated_request.refresh_from_db()
        self.assertEqual(self.unallocated_request.allocated, False)
        self.assertIsNone(self.unallocated_request.venue)
        self.assertIsNone(self.unallocated_request.day)
        self.assertIsNone(self.unallocated_request.tutor)

    def navigate_to_admin_dashboard(self, user: User):
        log_in_via_form(self.driver, self.live_server_url, user.username, 'Password123')
        admin_dash_url = f"{self.live_server_url}{reverse('admin_dash')}"
        self.driver.get(admin_dash_url)
        wait(self.driver)

    def navigate_to_view_users_page(self, user: User):
        log_in_via_form(self.driver, self.live_server_url, user.username, 'Password123')
        url = f"{self.live_server_url}{reverse('view_all_users')}"
        self.driver.get(url)
        wait(self.driver)

    def navigate_to_view_requests_page(self, user: User):
        log_in_via_form(self.driver, self.live_server_url, user.username, 'Password123')
        self.driver.get(f"{self.live_server_url}{reverse('view_requests')}")
        wait(self.driver)

    def navigate_to_requests_page_and_retrieve_allocate_button(self, user: User) -> WebElement:
        self.navigate_to_view_requests_page(user)
        try:
            button = wait_for_clickable(self.driver, wait_for_element(self.driver, By.ID,
                                                                      f"id_allocation_button_{self.unallocated_request.id}"))
            self.assertTrue(button.is_displayed())
            self.assertTrue(button.is_enabled())
        except NoSuchElementException:
            self.fail("Allocation button was not found in requests page (unexpected error).")

        return button if button else None
