import time

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.shortcuts import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select
from webdriver_manager.firefox import GeckoDriverManager

from code_tutors.test_selenium_functional_tests import wait
from user_system.fixtures.create_test_users import create_test_users
from user_system.models import User


class TestFunctionalRegistration(StaticLiveServerTestCase):
    def setUp(self):
        self.driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))

    def tearDown(self):
        self.driver.quit()

    def test_user_can_register(self):
        self.driver.get(f"{self.live_server_url}{reverse('sign_up')}")
        fields = self.get_user_form_fields()
        self.fill_out_fields(fields)
        wait(self.driver)
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
        username_input = self.driver.find_element(By.NAME, "username")
        first_name_input = self.driver.find_element(By.NAME, "first_name")
        last_name_input = self.driver.find_element(By.NAME, "last_name")
        email_input = self.driver.find_element(By.NAME, "email")
        user_type_input = self.driver.find_element(By.NAME, "user_type")
        password_input = self.driver.find_element(By.NAME, "new_password")
        confirm_password_input = self.driver.find_element(By.NAME, "password_confirmation")
        submit = self.driver.find_element(By.ID, "id_submit_button_sign_up")

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

        self.driver.execute_script("arguments[0].scrollIntoView(true);", submit)
        time.sleep(0.1)
        submit.click()


class TestFunctionalUserSystem(StaticLiveServerTestCase):
    def setUp(self):
        self.driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
        create_test_users()
        self.student = User.objects.get(user_type='Student')
        self.tutor = User.objects.get(user_type='Tutor')
        self.admin = User.objects.get(user_type='Admin')

    def tearDown(self):
        self.driver.quit()

    def test_user_can_log_in(self):
        self.log_in_via_form(self.student.username, 'Password123')
        wait(self.driver)
        self.assertEqual(self.driver.current_url,
                         f"{self.live_server_url}{reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)}")

    def test_student_can_update_their_maximum_hourly_rate(self):
        self.log_in_via_form(self.student.username, 'Password123')
        self.driver.get(f"{self.live_server_url}{reverse('profile')}")
        time.sleep(0.5)

        max_rate_input = self.driver.find_element(By.ID, "id_student_max_rate")
        self.populate_rate_field(max_rate_input)

        wait(self.driver)
        self.student.refresh_from_db()
        self.assertEqual(self.student.student_max_rate, 15.00)

    def test_tutor_can_set_their_hourly_rate(self):
        self.log_in_via_form(self.tutor.username, 'Password123')
        self.driver.get(f"{self.live_server_url}{reverse('profile')}")
        time.sleep(0.5)

        hourly_rate_input = self.driver.find_element(By.ID, "id_hourly_rate")
        self.populate_rate_field(hourly_rate_input)

        wait(self.driver)
        self.tutor.refresh_from_db()
        self.assertEqual(self.tutor.hourly_rate, 15.00)

    # def test_tutor_can_add_a_knowledge_area_to_their_profile(self):
    #     self.log_in_via_form(self.tutor.username, 'Password123')
    #     self.driver.get(f"{self.live_server_url}{reverse('profile')}")
    #     time.sleep(0.5)
    #
    #     self.driver.find_element(By.ID, "id_add_knowledge_areas").click()
    #     time.sleep(0.5)
    #
    #     self.assertEqual(self.driver.current_url, f"{self.live_server_url}{reverse('add_knowledge_areas')}")
    #     select = Select(self.driver.find_element(By.ID, "id_subject"))
    #     select.select_by_visible_text("C++")
    #
    #     self.driver.find_element(By.ID, "id_add_knowledge_area").click()
    #     time.sleep(0.5)
    #
    #     self.assertTrue(KnowledgeArea.objects.filter(user=self.tutor, subject='C++').exists())

    # -- HELPERS --#

    def log_in_via_form(self, username: str, password: str):
        """
        Automates the login process for a user in Selenium.

        Args:
            username (str): The username of the user.
            password (str): The password of the user.
        """
        self.driver.get(f"{self.live_server_url}{reverse('log_in')}")
        wait(self.driver)

        username_input = self.driver.find_element(By.ID, "id_username")
        password_input = self.driver.find_element(By.ID, "id_password")
        login_button = self.driver.find_element(By.ID, "id_submit_log_in_page")
        username_input.send_keys(username)
        password_input.send_keys(password)
        login_button.click()

        wait(self.driver)
        self.assertIn("dashboard", self.driver.page_source.lower())

    def populate_rate_field(self, field: WebElement):
        time.sleep(0.1)
        field.clear()
        field.send_keys("15.00")
        submit = self.driver.find_element(By.ID, "id_submit_profile_page")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", submit)
        submit.click()
