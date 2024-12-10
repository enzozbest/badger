"""Unit tests_user_system of the user form."""
from decimal import Decimal

from django import forms
from django.test import TestCase

from user_system.fixtures.create_test_users import create_test_users
from user_system.forms.user_form import UserForm
from user_system.models.user_model import User


class UserFormTestCase(TestCase):
    """Unit tests_user_system of the user form."""

    def setUp(self):
        create_test_users()
        self.form_input = {
            'first_name': 'Enzo',
            'last_name': 'Bestetti',
            'username': '@enzozbest',
            'email': 'enzozbest@example.org',
        }
        self.tutor_user = User.objects.get(
            user_type=User.ACCOUNT_TYPE_TUTOR,
        )
        self.student_user = User.objects.get(
            user_type=User.ACCOUNT_TYPE_STUDENT,
        )
        self.client.force_login(self.tutor_user)

    def test_form_has_necessary_fields(self):
        form = UserForm()
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('username', form.fields)
        self.assertIn('email', form.fields)
        email_field = form.fields['email']
        self.assertTrue(isinstance(email_field, forms.EmailField))

    def test_valid_user_form(self):
        form = UserForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_uses_model_validation(self):
        self.form_input['username'] = 'badusername'
        form = UserForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        user = User.objects.get(username='@johndoe')
        form = UserForm(instance=user, data=self.form_input)
        before_count = User.objects.count()
        self.assertTrue(form.is_valid(), msg=form.errors)
        form.save()
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(user.username, '@enzozbest')
        self.assertEqual(user.first_name, 'Enzo')
        self.assertEqual(user.last_name, 'Bestetti')
        self.assertEqual(user.email, 'enzozbest@example.org')

    def test_hourly_rate_field_visible_for_tutors(self):
        form = UserForm(instance=self.tutor_user)
        self.assertIn('hourly_rate', form.fields)
        self.assertEqual(form.fields['hourly_rate'].widget.attrs['placeholder'], "Enter your hourly rate e.g., 22.50")

    def test_hourly_rate_field_not_visible_to_students(self):
        self.client.force_login(self.student_user)
        form = UserForm(instance=self.student_user)
        self.assertNotIn('hourly_rate', form.fields)

    def test_hourly_rate_is_saved_correctly(self):
        data = {
            'first_name': self.tutor_user.first_name,
            'last_name': self.tutor_user.last_name,
            'username': self.tutor_user.username,
            'email': self.tutor_user.email,
            'user_type': self.tutor_user.user_type,
            'hourly_rate': Decimal('20.00'),  # Update hourly rate
        }
        form = UserForm(data=data, instance=self.tutor_user)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(self.tutor_user.hourly_rate, Decimal('20.00'))

    def test_hourly_rate_invalid_value(self):
        data = {
            'first_name': self.tutor_user.first_name,
            'last_name': self.tutor_user.last_name,
            'username': self.tutor_user.username,
            'email': self.tutor_user.email,
            'user_type': self.tutor_user.user_type,
            'hourly_rate': -50,  # Invalid value
        }
        form = UserForm(data=data, instance=self.tutor_user)
        self.assertFalse(form.is_valid())
        self.assertIn('hourly_rate', form.errors)
        self.assertEqual(form.errors['hourly_rate'][0], "Hourly rate must be a positive number!")

    def test_hourly_rate_default_value(self):
        new_tutor = User.objects.create_user(
            first_name="new",
            last_name="tutor",
            username="@newtutor",
            email="newtutor@example.com",
            password="Password123",
            user_type=User.ACCOUNT_TYPE_TUTOR,
        )
        form = UserForm(instance=new_tutor)
        self.assertEqual(form.instance.hourly_rate, 0.00)

    def test_only_students_can_set_maximum_hourly_rate(self):
        self.client.force_login(self.student_user)
        form = UserForm(instance=self.student_user)
        self.assertIn('student_max_rate', form.fields)

    def test_tutors_cannot_see_student_max_rate_field(self):
        self.client.force_login(self.tutor_user)
        form = UserForm(instance=self.tutor_user)
        self.assertNotIn('student_max_rate', form.fields)

    def test_admins_cannot_see_hourly_rate_or_max_rate_fields(self):
        admin = User.objects.get(user_type='Admin')
        self.client.force_login(admin)
        form = UserForm(instance=admin)
        self.assertNotIn('student_max_rate', form.fields)
        self.assertNotIn('hourly_rate', form.fields)

    def test_max_student_rate_is_saved_correctly(self):
        data = {
            'first_name': self.student_user.first_name,
            'last_name': self.student_user.last_name,
            'username': self.student_user.username,
            'email': self.student_user.email,
            'user_type': self.student_user.user_type,
            'student_max_rate': Decimal('20.00'),
        }
        self.client.force_login(self.student_user)
        form = UserForm(data=data, instance=self.student_user)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(self.student_user.student_max_rate, Decimal('20.00'))

    def test_student_max_rate_invalid_value(self):
        data = {
            'first_name': self.student_user.first_name,
            'last_name': self.student_user.last_name,
            'username': self.student_user.username,
            'email': self.student_user.email,
            'user_type': self.student_user.user_type,
            'student_max_rate': -50
        }
        self.client.force_login(self.student_user)
        form = UserForm(data=data, instance=self.student_user)
        self.assertFalse(form.is_valid())
        self.assertIn('student_max_rate', form.errors)
        self.assertEqual(form.errors['student_max_rate'][0], "Student max hourly rate must be a positive number!")

    def test_email_must_be_unique(self):
        data = {
            'first_name': self.tutor_user.first_name,
            'last_name': self.tutor_user.last_name,
            'username': self.tutor_user.username,
            'email': self.student_user.email,
            'user_type': self.tutor_user.user_type,
        }
        self.client.force_login(self.tutor_user)
        form = UserForm(instance=self.tutor_user, data=data)
        self.assertFalse(form.is_valid())
        self.assertRaises(ValueError, form.save)
