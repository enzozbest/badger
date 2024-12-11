import django.forms as forms

from request_handler.models import Venue
from user_system.models.day_model import Day
from user_system.models.user_model import User


class AllocationForm(forms.Form):
    """Class to represent the form which Admins use to allocate a student's tutoring request to a suitable tutor."""

    day1 = forms.ModelChoiceField(
        label='Choose a day for the allocation',
        queryset=Day.objects.none(),
        required=True
    )

    day2 = forms.ModelChoiceField(
        label='Choose a second day for the allocation',
        queryset=Day.objects.none(),
        required=False,
    )

    venue = forms.ModelChoiceField(queryset=Venue.objects.none(), label="Choose a Venue", required=False)

    tutor = forms.ModelChoiceField(queryset=User.objects.none(), label="Choose a Tutor", required=False)

    def __init__(self, *args, **kwargs):
        student = kwargs.pop('student')
        tutors = kwargs.pop('tutors', None)
        venues = kwargs.pop('venues')
        super().__init__(*args, **kwargs)
        self._set_form_fields(student, venues, tutors)

    def _set_form_fields(self, student, venues, tutors):
        day2_data = self._get_day_data(2)
        self._set_day1_field(student, day2_data)
        self._set_venue_field(venues)
        self._set_tutor_field(tutors)
        day1_data = self._get_day_data(1)
        self._set_day2_field(student, day1_data)

    def _set_venue_field(self, venues):
        self.fields['venue'].queryset = venues if venues else Venue.objects.none()
        self.fields['venue'].widget.attrs.update({'onchange': 'this.form.submit()'})

    def _set_day1_field(self, student: User, day2_data: str):
        self.fields[
            'day1'].queryset = student.availability.all() if not day2_data else student.availability.all().exclude(
            id=int(day2_data))
        self.fields['day1'].widget.attrs.update({'onchange': 'this.form.submit()'})

    def _set_tutor_field(self, tutors):
        self.fields['tutor'].queryset = tutors if tutors else User.objects.none()
        self.fields['tutor'].label_from_instance = self._get_tutor_label

    def _set_day2_field(self, student: User, day1_data: str):
        self.fields['day2'].queryset = student.availability.all().exclude(
            id=int(day1_data)) if day1_data else Day.objects.none()
        self.fields['day2'].widget.attrs.update({'onchange': 'this.form.submit()'})

    def _get_day_data(self, day_num: int):
        day_data = self.data.get(f'day{day_num}')
        if day_data and day_data == 'None':
            day_data = None
        return day_data

    def _get_tutor_label(self, obj):
        return f'{obj.username} - {obj.first_name} {obj.last_name}'
