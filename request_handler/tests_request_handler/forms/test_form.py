from django.test import TestCase
from django.forms import ModelMultipleChoiceField
from request_handler.forms import RequestForm
from request_handler.models import Day, Modality

class TestRequestForm(TestCase):
    def setUp(self):
        self.monday = Day.objects.create(day='Monday')
        self.wednesday = Day.objects.create(day='Wednesday')
        self.in_person = Modality.objects.create(mode='In Person')
        self.online = Modality.objects.create(mode='Online')

    def test_form_contains_required_fields(self):
        form = RequestForm()
        self.assertIn('available_days', form.fields)
        self.assertIn('term', form.fields)
        self.assertIn('knowledge_area', form.fields)
        self.assertIn('frequency', form.fields)
        self.assertIn('duration', form.fields)
        self.assertIn('mode_preference', form.fields)
        self.assertTrue(isinstance(form.fields['available_days'], ModelMultipleChoiceField))
        self.assertTrue(isinstance(form.fields['mode_preference'], ModelMultipleChoiceField))

    def test_form_accepts_valid_input(self):
        form_input = {
            'available_days': [self.monday.id, self.wednesday.id],
            'term': 'Easter',
            'knowledge_area': 'Scala',
            'frequency': 'Weekly',
            'duration': '1h',
            'mode_preference': [self.in_person.id, self.online.id]
        }
        form = RequestForm(data=form_input)
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_rejects_blank_available_days_field(self):
        invalid_input = {
            'available_days': [],
            'term': 'Easter',
            'knowledge_area': 'Scala',
            'frequency': 'Weekly',
            'duration': '1h',
            'mode_preference': [self.in_person.id, self.online.id]
        }
        form = RequestForm(data=invalid_input)
        self.assertFalse(form.is_valid())
        self.assertIn('available_days', form.errors)

    def test_form_rejects_blank_mode_preference_field(self):
        invalid_input = {
            'available_days': [self.monday.id, self.wednesday.id],
            'term': 'Easter',
            'knowledge_area': 'Scala',
            'frequency': 'Weekly',
            'duration': '1h',
            'mode_preference': []
        }
        form = RequestForm(data=invalid_input)
        self.assertFalse(form.is_valid())
        self.assertIn('mode_preference', form.errors)

    def test_form_rejects_blank_term_field(self):
        invalid_input = {
            'available_days': [self.monday.id, self.wednesday.id],
            'term': '',
            'knowledge_area': 'Scala',
            'frequency': 'Weekly',
            'duration': '1h',
            'mode_preference': [self.in_person.id, self.online.id]
        }
        form = RequestForm(data=invalid_input)
        self.assertFalse(form.is_valid())
        self.assertIn('term', form.errors)

    def test_form_rejects_blank_knowledge_area_field(self):
        invalid_input = {
            'available_days': [self.monday.id, self.wednesday.id],
            'term': 'Easter',
            'knowledge_area': '',
            'frequency': 'Weekly',
            'duration': '1h',
            'mode_preference': [self.in_person.id, self.online.id]
        }
        form = RequestForm(data=invalid_input)
        self.assertFalse(form.is_valid())
        self.assertIn('knowledge_area', form.errors)

    def test_form_rejects_blank_frequency_field(self):
        invalid_input = {
            'available_days': [self.monday.id, self.wednesday.id],
            'term': 'Easter',
            'knowledge_area': 'Scala',
            'frequency': '',
            'duration': '1h',
            'mode_preference': [self.in_person.id, self.online.id]
        }
        form = RequestForm(data=invalid_input)
        self.assertFalse(form.is_valid())
        self.assertIn('frequency', form.errors)

    def test_form_rejects_blank_duration_field(self):
        invalid_input = {
            'available_days': [self.monday.id, self.wednesday.id],
            'term': 'Easter',
            'knowledge_area': 'Scala',
            'frequency': 'Weekly',
            'duration': '',
            'mode_preference': [self.in_person.id, self.online.id]
        }
        form = RequestForm(data=invalid_input)
        self.assertFalse(form.is_valid())
        self.assertIn('duration', form.errors)