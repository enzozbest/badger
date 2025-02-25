from django.core.exceptions import ValidationError
from django.test import TestCase


class RequestModelTest(TestCase):
    def setUp(self):
        from user_system.models.user_model import User
        from request_handler.models.request_model import Request
        from request_handler.models.venue_model import Venue

        self.user = User.objects.create_user(username='@johndoe', email='johndoe@example.org', password='Password123')
        self.online = Venue.objects.create(venue='Online')
        self.in_person = Venue.objects.create(venue='In Person')
        self.request = Request.objects.create(student=self.user, term='Easter', knowledge_area='Scala',
                                              duration='1h', frequency='Weekly')
        self.request.venue_preference.add(self.in_person, self.online)
        self.tutor = User.objects.create_user(username='@janedoe', email='janedoe@example.org', password='Password123',
                                              first_name='Jane', last_name='Doe')

    def test_str_method_venue_preference_exists(self):
        s = str(self.request)
        self.assertEqual(s, (f'Student: johndoe@example.org'
                             f'\n Knowledge Area: Scala'
                             f'\n Term: Easter'
                             f'\n Frequency: Weekly'
                             f'\n Duration: 1h'
                             f'\n Venue Preference: Online, In Person'
                             f'\n Allocated?: No'
                             f'\n Tutor: -'
                             f'\n Late: False'
                             f'\n Recurring?: False'))

    def test_str_method_venue_preference_blank(self):
        self.request.venue_preference.clear()
        s = str(self.request)
        self.assertEqual(s, (f'Student: johndoe@example.org'
                             f'\n Knowledge Area: Scala'
                             f'\n Term: Easter'
                             f'\n Frequency: Weekly'
                             f'\n Duration: 1h'
                             f'\n Venue Preference: No venue preference set!'
                             f'\n Allocated?: No'
                             f'\n Tutor: -'
                             f'\n Late: False'
                             f'\n Recurring?: False'))

    def test_student_email_student_is_none(self):
        self.request.student = None
        s_email = self.request.student_email
        self.assertIsNone(s_email)

    def test_student_email_student_exists(self):
        s_email = self.request.student_email
        self.assertEqual(s_email, 'johndoe@example.org')

    def test_tutor_full_name_property(self):
        self.request.tutor = self.tutor
        t_name = self.request.tutor_name
        self.assertEqual(t_name, 'Jane Doe')

    def test_valid_model(self):
        try:
            self.request.full_clean()
        except ValidationError:
            self.fail('Request should have been valid.')

    def test_allocated(self):
        self.request.allocated = True
        self.request.save()
        self.request.refresh_from_db()
        str(self.request)
        self.assertEqual(self.request.allocated_string, "Yes")

    def test_unallocated(self):
        self.request.allocated = False
        str(self.request)
        self.assertEqual(self.request.allocated_string, "No")

    def test_tutor_allocated(self):
        self.request.tutor = self.tutor
        str(self.request)
        self.assertEqual(self.request.tutor_name, self.tutor.first_name + " " + self.tutor.last_name)

    def test_tutor_unallocated(self):
        self.request.tutor = None
        str(self.request)
        self.assertEqual(self.request.tutor_name_string, "-")

    def test_student_field_cannot_be_blank(self):
        self.request.student = None
        with self.assertRaises(AttributeError):
            self.request.student.email

    def test_term_field_cannot_be_blank(self):
        self.request.term = ''
        with self.assertRaises(ValidationError):
            self.request.full_clean()

    def test_duration_field_cannot_be_blank(self):
        self.request.duration = ''
        with self.assertRaises(ValidationError):
            self.request.full_clean()

    def test_frequency_field_cannot_be_blank(self):
        self.request.frequency = ''
        with self.assertRaises(ValidationError):
            self.request.full_clean()

    def test_knowledge_area_field_cannot_be_blank(self):
        self.request.knowledge_area = ''
        with self.assertRaises(ValidationError):
            self.request.full_clean()

    def test_venue_preference_field_cannot_be_empty(self):
        self.request.venue_preference.clear()
        with self.assertRaises(ValidationError):
            self.request.full_clean()

    def test_knowledge_area_length_constraints(self):
        self.request.knowledge_area = 'a' * 256
        with self.assertRaises(ValidationError):
            self.request.full_clean()

    # Do the same for all other CharFields:
    def test_duration_length_constraints(self):
        self.request.duration = 'a' * 256
        with self.assertRaises(ValidationError):
            self.request.full_clean()

    def test_frequency_length_constraints(self):
        self.request.frequency = 'a' * 256
        with self.assertRaises(ValidationError):
            self.request.full_clean()

    def test_term_length_constraints(self):
        self.request.term = 'a' * 256
        with self.assertRaises(ValidationError):
            self.request.full_clean()

    def test_is_recurring_default(self):
        self.assertFalse(self.request.is_recurring)

    def test_is_recurring_set_to_true(self):
        """Ensure is_recurring can be set to True."""
        self.request.is_recurring = True
        self.assertTrue(self.request.is_recurring)
