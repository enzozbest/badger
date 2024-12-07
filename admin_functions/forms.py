import django.forms as forms

from request_handler.models import Venue
from user_system.models import Day, User


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

        # Manually populate some fields based on what the tutoring request specifies

        day2_data = self.data.get('day2')
        if day2_data and day2_data == 'None':
            day2_data = None

        self.fields[
            'day1'].queryset = student.availability.all() if not day2_data else student.availability.all().exclude(
            id=int(day2_data))
        self.fields['day1'].widget.attrs.update({'onchange': 'this.form.submit()'})

        self.fields['venue'].queryset = venues if venues else Venue.objects.none()
        self.fields['venue'].widget.attrs.update({'onchange': 'this.form.submit()'})

        self.fields['tutor'].queryset = tutors if tutors else User.objects.none()
        self.fields['tutor'].label_from_instance = self.get_tutor_label

        day1_data = self.data.get('day1')
        if day1_data and day1_data == 'None':
            day1_data = None

        self.fields['day2'].queryset = student.availability.all().exclude(
            id=int(day1_data)) if day1_data else Day.objects.none()
        self.fields['day2'].widget.attrs.update({'onchange': 'this.form.submit()'})

    def get_tutor_label(self, obj):
        return f'{obj.username} - {obj.first_name} {obj.last_name}'
