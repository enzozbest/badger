from django.db.models import QuerySet
from django.test import TestCase

from admin_functions.forms import AllocationForm
from admin_functions.views.allocate_requests import get_venue_preference
from request_handler.fixtures.create_test_requests import create_test_requests
from request_handler.models.request_model import Request
from user_system.fixtures.create_test_users import create_test_users
from user_system.models.user_model import User


class TestForms(TestCase):
    def setUp(self):
        create_test_users()
        create_test_requests()
        self.unallocated_request = Request.objects.get(allocated=False)
        self.student = User.objects.get(user_type='Student')
        self.tutor = User.objects.get(user_type='Tutor')
        self.venues = get_venue_preference(self.unallocated_request.venue_preference)

    def test_day2_data_is_none(self):
        form_data = {'day2': 'None'}
        form = AllocationForm(data=form_data, student=self.student, venues=self.venues, tutors=QuerySet(self.tutor))
        self.assertQuerysetEqual(form.fields['day1'].queryset.order_by('id'),
                                 self.student.availability.all().order_by('id'), transform=lambda x: x)

    def test_day1_data_is_none(self):
        form_data = {'day1': 'None'}
        form = AllocationForm(data=form_data, student=self.student, venues=self.venues, tutors=QuerySet(self.tutor))
        self.assertQuerysetEqual(form.fields['day2'].queryset, [])

    def test_get_tutor_label(self):
        form = AllocationForm(data={}, student=self.student, venues=self.venues, tutors=QuerySet(self.tutor))
        self.assertEqual(form.fields['tutor'].label_from_instance(self.tutor), '@janedoe - Jane Doe')
