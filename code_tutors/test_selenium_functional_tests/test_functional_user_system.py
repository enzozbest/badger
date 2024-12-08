import time

from django.conf import settings
from django.contrib.sessions.models import Session
from django.shortcuts import reverse
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait

from user_system.fixtures.create_test_users import create_test_users
from user_system.models import User


class TestFunctionalUserSystem(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        cls.driver = webdriver.Chrome()
        cls.driver.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def test_user_can_register(self):
        # Navigate to the registration page
        self.driver.get(f"{self.live_server_url}{reverse('sign_up')}")  # Update with the actual URL path

        # Fill out the registration form
        username_input = self.driver.find_element(By.NAME, "username")
        first_name_input = self.driver.find_element(By.NAME, "first_name")
        last_name_input = self.driver.find_element(By.NAME, "last_name")
        email_input = self.driver.find_element(By.NAME, "email")
        user_type_input = self.driver.find_element(By.NAME, "user_type")
        password_input = self.driver.find_element(By.NAME, "new_password")
        confirm_password_input = self.driver.find_element(By.NAME, "password_confirmation")

        username_input.send_keys("@enzozbest")
        first_name_input.send_keys("Enzo")
        last_name_input.send_keys("Bestetti")

        email_input.send_keys("enzozbest@example.com")
        usertype = Select(user_type_input)
        usertype.select_by_visible_text("Student")
        password_input.send_keys("Password123")
        confirm_password_input.send_keys("Password123")
        confirm_password_input.send_keys(Keys.RETURN)

        time.sleep(0.1)
        self.assertEqual(
            self.driver.current_url,
            f"{self.live_server_url}{reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)}"
        )
        self.assertTrue(User.objects.filter(username='@enzozbest').exists())
        enzozbest = User.objects.get(username='@enzozbest')
        self.assertTrue(enzozbest.first_name == "Enzo")
        self.assertTrue(enzozbest.last_name == "Bestetti")
        self.assertTrue(enzozbest.email == "enzozbest@example.com")
        self.assertTrue(enzozbest.user_type == "Student")

    def test_user_can_log_in(self):
        create_test_users()
        self.driver.get(f"{self.live_server_url}{reverse('log_in')}")
        username_input = self.driver.find_element(By.NAME, "username")
        password_input = self.driver.find_element(By.NAME, "password")

        username_input.send_keys("@johndoe")
        password_input.send_keys("Password123")
        username_input.send_keys(Keys.RETURN)

        time.sleep(0.1)
        self.assertEqual(
            self.driver.current_url,
            f"{self.live_server_url}{reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)}"
        )

    def test_user_can_update_their_password(self):
        create_test_users()
        student = User.objects.get(user_type='Student')
        self.log_in(student.username, 'Password123')
        self.driver.get(f"{self.live_server_url}{reverse('password')}")

        password_input = self.driver.find_element(By.NAME, "new_password")
        password_confirmation_input = self.driver.find_element(By.NAME, "password_confirmation")
        current_password_input = self.driver.find_element(By.NAME, "password")

        self.assertTrue(
            student.check_password("Password123"))  # Confirm current password is as expected

        password_input.send_keys("Password1234")
        password_confirmation_input.send_keys("Password1234")
        current_password_input.send_keys("Password123")
        current_password_input.send_keys(Keys.RETURN)

        time.sleep(0.5)
        student.refresh_from_db()
        self.assertTrue(
            student.check_password("Password1234"))  # Confirm password was changed successfully

    def log_in(self, username: str, password: str):
        """
        Automates the login process for a user in Selenium.

        Args:
            username (str): The username of the user.
            password (str): The password of the user.
        """
        self.driver.get(f"{self.live_server_url}{reverse('log_in')}")

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )

        username_input = self.driver.find_element(By.NAME, "username")
        password_input = self.driver.find_element(By.NAME, "password")
        username_input.send_keys(username)
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)  # Submit the form

        WebDriverWait(self.driver, 10).until(
            EC.url_changes(f"{reverse('dashboard')}")
        )
        self.assertIn("dashboard", self.driver.page_source.lower())

    def get_logged_in_user(self) -> User:
        session_key = self.client.session.session_key
        session = Session.objects.get(session_key=session_key)
        session_data = session.get_decoded()
        user_id = session_data.get('_auth_user_id')
        return User.objects.get(id=user_id)
