import os
import time
from unittest import skipIf

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.shortcuts import reverse
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select

from code_tutors.test_selenium_functional_tests import log_in_via_form, wait, wait_for_clickable, wait_for_element
from user_system.fixtures.create_test_users import create_test_users
from user_system.models.knowledge_area_model import KnowledgeArea
from user_system.models.user_model import User


@skipIf(os.environ.get('GITHUB_ACTIONS') == 'true', 'These tests require headed browsers to work properly')
class TestFunctionalRegistration(StaticLiveServerTestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.maximize_window()

    def tearDown(self):
        self.driver.quit()

    def test_user_can_register(self):
        self.driver.get(f"{self.live_server_url}{reverse('sign_up')}")
        wait(self.driver)
        fields = self.get_user_form_fields()
        self.fill_out_fields(fields)
        self.assertEqual(
            self.driver.current_url,
            f"{self.live_server_url}{reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)}"
        )
        self.assertTrue(User.objects.filter(username='@enzozbest').exists())
        enzozbest = User.objects.get(username='@enzozbest')
        self.assertEqual(enzozbest.first_name, "Enzo")
        self.assertEqual(enzozbest.last_name, "Bestetti")
        self.assertEqual(enzozbest.email, "enzozbest@example.com")
        self.assertEqual(enzozbest.user_type, "Student")

    # -- HELPERS --#
    def get_user_form_fields(self):
        username_input = wait_for_element(self.driver, By.ID, "id_username")
        first_name_input = wait_for_element(self.driver, By.ID, "id_first_name")
        last_name_input = wait_for_element(self.driver, By.ID, "id_last_name")
        email_input = wait_for_element(self.driver, By.ID, "id_email")
        user_type_input = wait_for_element(self.driver, By.ID, "id_user_type")
        password_input = wait_for_element(self.driver, By.ID, "id_new_password")
        confirm_password_input = wait_for_element(self.driver, By.ID, "id_password_confirmation")
        submit = wait_for_clickable(self.driver, wait_for_element(self.driver, By.ID, "id_submit_button_sign_up"))

        return (username_input, first_name_input, last_name_input, email_input, user_type_input,
                password_input, confirm_password_input, submit)

    def fill_out_fields(self, fields: tuple):
        (username_input, first_name_input, last_name_input, email_input,
         user_type_input, password_input, confirm_password_input, submit) = fields

        username_input.send_keys("@enzozbest")
        first_name_input.send_keys("Enzo")
        last_name_input.send_keys("Bestetti")
        email_input.send_keys("enzozbest@example.com")
        usertype = Select(user_type_input)
        usertype.select_by_visible_text("Student")
        password_input.send_keys("Password123")
        confirm_password_input.send_keys("Password123")
        submit.click()


@skipIf(os.environ.get('GITHUB_ACTIONS') == 'true', 'These tests require headed browsers to work properly')
class TestFunctionalUserSystem(StaticLiveServerTestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.maximize_window()

        create_test_users()
        self.student = User.objects.get(user_type='Student')
        self.tutor = User.objects.get(user_type='Tutor')
        self.admin = User.objects.get(user_type='Admin')

    def tearDown(self):
        self.driver.quit()

    def test_user_can_log_in(self):
        log_in_via_form(self.driver, self.live_server_url, self.student.username, 'Password123')
        wait(self.driver)
        self.assertEqual(self.driver.current_url,
                         f"{self.live_server_url}{reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)}")

    def test_logging_in_with_wrong_credentials_does_not_log_in(self):
        log_in_via_form(self.driver, self.live_server_url, self.student.username, 'WrongPassword')
        self.assertNotEqual(self.driver.current_url,
                            f"{self.live_server_url}{reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)}")
        self.assertEqual(self.driver.current_url, f"{self.live_server_url}{reverse('log_in')}")
        self.assertIn("The credentials provided were invalid!", self.driver.page_source)

    def test_student_can_update_their_maximum_hourly_rate(self):
        log_in_via_form(self.driver, self.live_server_url, self.student.username, 'Password123')
        self.driver.get(f"{self.live_server_url}{reverse('profile')}")
        wait(self.driver)
        max_rate_input = wait_for_element(self.driver, By.ID, "id_student_max_rate")
        self.populate_rate_field(max_rate_input)
        wait(self.driver)
        self.student.refresh_from_db()
        self.assertEqual(self.student.student_max_rate, 15.00)

    def test_tutors_cannot_update_maximum_hourly_rate(self):
        log_in_via_form(self.driver, self.live_server_url, self.tutor.username, 'Password123')
        self.driver.get(f"{self.live_server_url}{reverse('profile')}")
        wait(self.driver)
        with self.assertRaises(NoSuchElementException):
            self.driver.find_element(By.ID, "id_student_max_rate")

    def test_tutor_can_set_their_hourly_rate(self):
        log_in_via_form(self.driver, self.live_server_url, self.tutor.username, 'Password123')
        self.driver.get(f"{self.live_server_url}{reverse('profile')}")
        wait(self.driver)

        hourly_rate_input = wait_for_element(self.driver, By.ID, "id_hourly_rate")
        self.populate_rate_field(hourly_rate_input)
        wait(self.driver)
        self.tutor.refresh_from_db()
        self.assertEqual(self.tutor.hourly_rate, 15.00)

    def test_students_cannot_set_an_hourly_rate(self):
        log_in_via_form(self.driver, self.live_server_url, self.student.username, 'Password123')
        self.driver.get(f"{self.live_server_url}{reverse('profile')}")
        wait(self.driver)

        with self.assertRaises(NoSuchElementException):
            self.driver.find_element(By.ID, "id_hourly_rate")

    def test_user_can_change_their_password(self):
        log_in_via_form(self.driver, self.live_server_url, self.student.username, 'Password123')
        self.driver.get(f"{self.live_server_url}{reverse('password')}")
        wait(self.driver)
        self.populate_password_fields(self.get_password_change_fields())
        wait(self.driver)
        self.student.refresh_from_db()
        self.assertTrue(self.student.check_password("NewPassword123"))

    def test_tutor_can_add_a_knowledge_area_to_their_profile(self):
        self.navigate_to_knowledge_areas_page()
        self.assertEqual(self.driver.current_url, f"{self.live_server_url}{reverse('add_knowledge_areas')}")
        select = Select(wait_for_element(self.driver, By.ID, "id_subject"))
        select.select_by_visible_text("C++")

        wait_for_clickable(self.driver, wait_for_element(self.driver, By.ID, "id_add_knowledge_area")).click()
        self.assertTrue(KnowledgeArea.objects.filter(user=self.tutor, subject='C++').exists())

    def test_tutor_can_delete_a_knowledge_area_from_their_profile(self):
        self.navigate_to_knowledge_areas_page()
        self.assertEqual(self.driver.current_url, f"{self.live_server_url}{reverse('add_knowledge_areas')}")
        area = KnowledgeArea.objects.filter(user=self.tutor).first()
        delete_link = wait_for_clickable(self.driver,
                                         wait_for_element(self.driver, By.ID, f"id_delete_knowledge_area_{area.id}"))
        delete_link.click()
        wait(self.driver)
        self.assertFalse(KnowledgeArea.objects.filter(id=area.id).exists())

    def test_users_cannot_change_their_account_type(self):
        log_in_via_form(self.driver, self.live_server_url, self.student.username, 'Password123')
        self.driver.get(f"{self.live_server_url}{reverse('profile')}")
        wait(self.driver)
        account_type = wait_for_element(self.driver, By.ID, "id_user_type")
        self.assertFalse(account_type.is_enabled())

    # -- HELPERS --#

    def populate_rate_field(self, field: WebElement):
        field.clear()
        field.send_keys("15.00")
        submit = wait_for_clickable(self.driver, wait_for_element(self.driver, By.ID, "id_submit_profile_page"))
        time.sleep(1)
        submit.click()
        wait(self.driver)

    def navigate_to_knowledge_areas_page(self):
        log_in_via_form(self.driver, self.live_server_url, self.tutor.username, 'Password123')
        self.driver.get(f"{self.live_server_url}{reverse('profile')}")
        wait(self.driver)
        button = wait_for_clickable(self.driver, wait_for_element(self.driver, By.ID, "id_add_knowledge_areas"))
        time.sleep(1)
        button.click()
        wait(self.driver)

    def get_password_change_fields(self) -> tuple:
        new_password_input = wait_for_element(self.driver, By.ID, "id_new_password")
        password_confirmation_input = wait_for_element(self.driver, By.ID, "id_password_confirmation")
        current_password_input = wait_for_element(self.driver, By.ID, "id_password")
        submit_button = wait_for_clickable(self.driver, wait_for_element(self.driver, By.ID, "id_change_password"))
        return new_password_input, password_confirmation_input, current_password_input, submit_button

    def populate_password_fields(self, fields: tuple):
        new_password_input, password_confirmation_input, current_password_input, submit_button = fields
        new_password_input.send_keys("NewPassword123")
        password_confirmation_input.send_keys("NewPassword123")
        current_password_input.send_keys("Password123")
        submit_button.click()
