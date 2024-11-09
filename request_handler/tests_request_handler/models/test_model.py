from django.core.exceptions import ValidationError
from django.test import TestCase

class RequestModelTest(TestCase):
    def setUp(self):
        from tutorials.models import User
        from request_handler.models import Request, Day, Modality

        self.user = User.objects.create_user(username='@johndoe', email='johndoe@example.org', password='Password123')
        self.monday = Day.objects.create(day='Monday')
        self.wednesday = Day.objects.create(day='Wednesday')
        self.in_person = Modality.objects.create(mode='In Person')
        self.online = Modality.objects.create(mode='Online')
        self.request = Request.objects.create(student=self.user, term='Easter', knowledge_area='Scala',
                               duration='1h', frequency='Weekly')
        self.request.availability.add(self.monday, self.wednesday)
        self.request.venue_preference.add(self.in_person, self.online)

    def test_str_method_availability_exists(self):
        s  = str(self.request)
        self.assertEqual(s, (f'Student: johndoe@example.org'
                f'\n Knowledge Area: Scala'
                f'\n Availability: Monday, Wednesday'
                f'\n Term: Easter'
                f'\n Frequency: Weekly'
                f'\n Duration: 1h'
                f'\n Venue Preference: In Person, Online'))

    def test_str_method_availability_blank(self):
        self.request.availability.clear()
        s  = str(self.request)
        self.assertEqual(s, (f'Student: johndoe@example.org'
                f'\n Knowledge Area: Scala'
                f'\n Availability: No availability set!'
                f'\n Term: Easter'
                f'\n Frequency: Weekly'
                f'\n Duration: 1h'
                f'\n Venue Preference: In Person, Online'))

    def test_str_method_venue_preference_exists(self):
        s  = str(self.request)
        self.assertEqual(s, (f'Student: johndoe@example.org'
                f'\n Knowledge Area: Scala'
                f'\n Availability: Monday, Wednesday'
                f'\n Term: Easter'
                f'\n Frequency: Weekly'
                f'\n Duration: 1h'
                f'\n Venue Preference: In Person, Online'))

    def test_str_method_venue_preference_blank(self):
        self.request.venue_preference.clear()
        s = str(self.request)
        self.assertEqual(s, (f'Student: johndoe@example.org'
                f'\n Knowledge Area: Scala'
                f'\n Availability: Monday, Wednesday'
                f'\n Term: Easter'
                f'\n Frequency: Weekly'
                f'\n Duration: 1h'
                f'\n Venue Preference: No venue preference set!'))

    def test_student_email_student_is_none(self):
        self.request.student = None
        s_email = self.request.student_email
        self.assertIsNone(s_email)

    def test_student_email_student_exists(self):
        s_email = self.request.student_email
        self.assertEqual(s_email, 'johndoe@example.org')

    def test_valid_model(self):
        try:
            self.request.full_clean()
        except ValidationError:
            self.fail('Request should have been valid.')

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

    def test_availability_field_cannot_be_empty(self):
        self.request.availability.clear()
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

    #Do the same for all other CharFields:
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

