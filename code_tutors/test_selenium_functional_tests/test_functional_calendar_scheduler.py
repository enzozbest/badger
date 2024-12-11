import os
from unittest import skipIf

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.shortcuts import reverse
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from calendar_scheduler.models import Booking
from code_tutors.test_selenium_functional_tests import log_in_via_form, logout, wait, wait_for_clickable, \
    wait_for_element
from request_handler.fixtures.create_test_requests import create_test_requests
from request_handler.models import Request, Venue
from user_system.fixtures.create_test_users import create_test_users
from user_system.models.user_model import User


@skipIf(os.environ.get('GITHUB_ACTIONS') == 'true', 'These tests require headed browsers to work properly')
class TestFunctionalCalendarScheduler(StaticLiveServerTestCase):
    def setUp(self):
        create_test_users()
        self.admin = User.objects.get(user_type=User.ACCOUNT_TYPE_ADMIN)
        self.student = User.objects.get(user_type=User.ACCOUNT_TYPE_STUDENT)
        self.tutor = User.objects.get(user_type=User.ACCOUNT_TYPE_TUTOR)

        Venue.objects.get_or_create(venue="In Person")
        Venue.objects.get_or_create(venue="Online")
        Venue.objects.get_or_create(venue="No Preference")

        create_test_requests()
        self.allocated_request = Request.objects.get(allocated=True)
        self.unallocated_request = Request.objects.get(allocated=False)

        self.driver = webdriver.Firefox()
        self.driver.maximize_window()

    def tearDown(self):
        self.driver.quit()

    def test_bookings_are_made_upon_tutor_accept_request(self):
        self.accept_request()
        self.assertEqual(Booking.objects.count(), 15)

    def test_bookings_are_not_made_upon_student_attempts_to_accept_request(self):
        log_in_via_form(self.driver, self.live_server_url, self.student.username, 'Password123')
        self.driver.get(
            f"{self.live_server_url}{reverse('accept_request', kwargs={'request_id': self.allocated_request.pk})}")
        wait(self.driver)
        self.assertEqual(Booking.objects.count(), 0)

    def test_bookings_are_not_made_upon_admin_attempts_to_accept_request(self):
        log_in_via_form(self.driver, self.live_server_url, self.admin.username, 'Password123')
        self.driver.get(
            f"{self.live_server_url}{reverse('accept_request', kwargs={'request_id': self.allocated_request.pk})}")
        wait(self.driver)
        self.assertEqual(Booking.objects.count(), 0)

    def test_student_can_see_calendar_link_in_dashboard(self):
        log_in_via_form(self.driver, self.live_server_url, self.student.username, 'Password123')
        self.driver.get(f"{self.live_server_url}{reverse('dashboard')}")
        wait(self.driver)
        try:
            link = wait_for_clickable(self.driver, wait_for_element(self.driver, By.ID, 'id_view_student_calendar'))
            self.assertTrue(link.is_displayed())
            self.assertTrue(link.is_enabled())
        except NoSuchElementException:
            self.fail("Calendar link should have been visible")

    def test_tutor_can_see_calendar_link_in_dashboard(self):
        log_in_via_form(self.driver, self.live_server_url, self.tutor.username, 'Password123')
        self.driver.get(f"{self.live_server_url}{reverse('dashboard')}")
        wait(self.driver)
        try:
            link = wait_for_clickable(self.driver, wait_for_element(self.driver, By.ID, 'id_view_tutor_calendar'))
            self.assertTrue(link.is_displayed())
            self.assertTrue(link.is_enabled())
        except NoSuchElementException:
            self.fail("Calendar link should have been visible")

    def test_admin_cannot_see_links_for_individual_calendars(self):
        log_in_via_form(self.driver, self.live_server_url, self.admin.username, 'Password123')
        self.driver.get(f"{self.live_server_url}{reverse('dashboard')}")
        with self.assertRaises(NoSuchElementException):
            self.driver.find_element(By.ID, 'id_view_student_calendar')
        with self.assertRaises(NoSuchElementException):
            self.driver.find_element(By.ID, 'id_view_tutor_calendar')

    def test_tutor_can_see_the_tutor_calendar_and_bookings(self):
        self.accept_request()
        logout(self.driver, self.live_server_url)
        log_in_via_form(self.driver, self.live_server_url, self.tutor.username, 'Password123')
        self.driver.get(f"{self.live_server_url}{reverse('dashboard')}")
        wait(self.driver)

        link = wait_for_clickable(self.driver, wait_for_element(self.driver, By.ID, 'id_view_tutor_calendar'))
        link.click()
        self.assertEqual(self.driver.current_url, f"{self.live_server_url}{reverse('tutor_calendar')}")

    def test_student_can_see_the_student_calendar_and_bookings(self):
        self.accept_request()
        logout(self.driver, self.live_server_url)
        log_in_via_form(self.driver, self.live_server_url, self.student.username, 'Password123')
        self.driver.get(f"{self.live_server_url}{reverse('dashboard')}")
        wait(self.driver)

        link = wait_for_clickable(self.driver, wait_for_element(self.driver, By.ID, 'id_view_student_calendar'))
        link.click()
        self.assertEqual(self.driver.current_url, f"{self.live_server_url}{reverse('student_calendar')}")

    def test_student_cannot_see_the_tutor_calendar_and_bookings(self):
        self.accept_request()
        logout(self.driver, self.live_server_url)
        log_in_via_form(self.driver, self.live_server_url, self.student.username, 'Password123')
        self.driver.get(f"{self.live_server_url}{reverse('tutor_calendar')}")
        wait(self.driver)
        self.assertIn("Permission Denied".lower(), self.driver.page_source.lower())

    def test_tutor_cannot_see_the_student_calendar_and_bookings(self):
        self.accept_request()
        logout(self.driver, self.live_server_url)
        log_in_via_form(self.driver, self.live_server_url, self.tutor.username, 'Password123')
        self.driver.get(f"{self.live_server_url}{reverse('student_calendar')}")
        wait(self.driver)
        self.assertIn("Permission Denied".lower(), self.driver.page_source.lower())

    def accept_request(self):
        log_in_via_form(self.driver, self.live_server_url, self.tutor.username, 'Password123')
        self.driver.get(f"{self.live_server_url}{reverse('view_requests')}")
        wait(self.driver)
        try:
            button = wait_for_clickable(self.driver, wait_for_element(self.driver, By.ID,
                                                                      f"id_accept_request_{self.allocated_request.id}"))
            button.click()
            wait(self.driver)
        except NoSuchElementException:
            self.fail("Accept button was not found!")
