from django.test import TestCase
from django.forms import ModelMultipleChoiceField
from request_handler.forms import RequestForm
from request_handler.models import Venue
from user_system.models import Day
from datetime import datetime 

class TestRequestForm(TestCase):
    def setUp(self):
        self.monday = Day.objects.create(day='Monday')
        self.wednesday = Day.objects.create(day='Wednesday')
        self.in_person = Venue.objects.create(venue='In Person')
        self.online = Venue.objects.create(venue='Online')

    def test_form_contains_required_fields(self):
        form = RequestForm()
        self.assertIn('term', form.fields)
        self.assertIn('knowledge_area', form.fields)
        self.assertIn('frequency', form.fields)
        self.assertIn('duration', form.fields)
        self.assertIn('venue_preference', form.fields)
        self.assertTrue(isinstance(form.fields['venue_preference'], ModelMultipleChoiceField))

    def test_form_accepts_valid_input(self):
        form_input = {
            'availability': [self.monday.id, self.wednesday.id],
            'term': 'January',
            'knowledge_area': 'Scala',
            'frequency': 'Weekly',
            'duration': '1',
            'venue_preference': [self.in_person.id, self.online.id],
            'is_recurring': True
        }
        form = RequestForm(data=form_input)
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_rejects_blank_availability_field(self):
        invalid_input = {
            'availability': [],
            'term': 'Easter',
            'knowledge_area': 'Scala',
            'frequency': 'Weekly',
            'duration': '1',
            'venue_preference': [self.in_person.id, self.online.id],
            'is_recurring': False
        }
        form = RequestForm(data=invalid_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_mode_preference_field(self):
        invalid_input = {
            'term': 'Easter',
            'knowledge_area': 'Scala',
            'frequency': 'Weekly',
            'duration': '1',
            'venue_preference': [],
            'is_recurring': False
        }
        form = RequestForm(data=invalid_input)
        self.assertFalse(form.is_valid())
        self.assertIn('venue_preference', form.errors)

    def test_form_rejects_blank_term_field(self):
        invalid_input = {
            'availability': [self.monday.id, self.wednesday.id],
            'term': '',
            'knowledge_area': 'Scala',
            'frequency': 'Weekly',
            'duration': '1',
            'venue_preference': [self.in_person.id, self.online.id],
            'is_recurring': False
        }
        form = RequestForm(data=invalid_input)
        self.assertFalse(form.is_valid())
        self.assertIn('term', form.errors)

    def test_form_rejects_blank_knowledge_area_field(self):
        invalid_input = {
            'availability': [self.monday.id, self.wednesday.id],
            'term': 'Easter',
            'knowledge_area': '',
            'frequency': 'Weekly',
            'duration': '1',
            'venue_preference': [self.in_person.id, self.online.id],
            'is_recurring': False
        }
        form = RequestForm(data=invalid_input)
        self.assertFalse(form.is_valid())
        self.assertIn('knowledge_area', form.errors)

    def test_form_rejects_blank_frequency_field(self):
        invalid_input = {
            'availability': [self.monday.id, self.wednesday.id],
            'term': 'Easter',
            'knowledge_area': 'Scala',
            'frequency': '',
            'duration': '1',
            'venue_preference': [self.in_person.id, self.online.id],
            'is_recurring': False
        }
        form = RequestForm(data=invalid_input)
        self.assertFalse(form.is_valid())
        self.assertIn('frequency', form.errors)

    def test_form_rejects_blank_duration_field(self):
        invalid_input = {
            'availability': [self.monday.id, self.wednesday.id],
            'term': 'Easter',
            'knowledge_area': 'Scala',
            'frequency': 'Weekly',
            'duration': '',
            'venue_preference': [self.in_person.id, self.online.id],
            'is_recurring': False
        }
        form = RequestForm(data=invalid_input)
        self.assertFalse(form.is_valid())
        self.assertIn('duration', form.errors)
    
    def test_form_handles_is_recurring_correctly(self):
        invalid_input = {
            'availability': [self.monday.id, self.wednesday.id],
            'term': 'January',
            'knowledge_area': 'Scala',
            'frequency': 'Weekly',
            'duration': '1',
            'venue_preference': [self.in_person.id, self.online.id],
            'is_recurring': True
        }
        form = RequestForm(data=invalid_input)
        self.assertTrue(form.is_valid())
        self.assertTrue(form.cleaned_data['is_recurring'])

        invalid_input['is_recurring'] = False
        form = RequestForm(data=invalid_input)
        self.assertTrue(form.is_valid())
        self.assertFalse(form.cleaned_data['is_recurring'])

    def test_form_late_request_response(self):
        form_input = {
            'availability': [self.monday.id, self.wednesday.id],
            'term': '',
            'knowledge_area': 'Scala',
            'frequency': 'Weekly',
            'duration': '1',
            'venue_preference': [self.in_person.id, self.online.id],
            'is_recurring': False
        }
        #Purposefully choosing a late term
        if datetime.now().month >= 1 and datetime.now().month<5:
            form_input['term'] = 'January'
        elif datetime.now().month > 8 and datetime.now().month <= 12:
            form_input['term'] = 'September'
        elif datetime.now().month < 9 :
            form_input['term'] = 'May'

        form = RequestForm(data=form_input)

        self.assertTrue(form.is_valid())
        self.assertTrue(form.is_late_request())