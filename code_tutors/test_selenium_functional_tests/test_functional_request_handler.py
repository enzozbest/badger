import geckodriver_autoinstaller
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.shortcuts import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from code_tutors.test_selenium_functional_tests import log_in_via_form, wait, wait_for_clickable, wait_for_element
from request_handler.fixtures.create_test_requests import create_test_requests
from request_handler.models import Request, Venue
from user_system.fixtures.create_test_users import create_test_users
from user_system.models import User

geckodriver_autoinstaller.install()


class TestFunctionalRequestHandler(StaticLiveServerTestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
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
        self.create_request_via_form()

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

    def create_request_via_form(self):
        self.driver.get(f'{self.live_server_url}{reverse("create_request")}')
        wait(self.driver)
        self.populate_create_request_fields(self.get_create_request_fields())
        wait(self.driver)
        self.assertEqual(self.driver.current_url, f"{self.live_server_url}{reverse('request_success')}")
        self.assertTrue(Request.objects.filter(student=self.student).exists())

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
