import django.forms as forms

from user_system.models import Day, User


class AllocationForm(forms.Form):
    """Class to represent the form which Admins use to allocate a student's tutoring request to a suitable tutor."""

    day = forms.ModelChoiceField(
        label='Choose a day for the allocation',
        queryset=Day.objects.none(),
    )
    venue = forms.ChoiceField(choices=[], label="Choose a Venue")
    tutor = forms.ModelChoiceField(queryset=User.objects.none(), label="Choose a Tutor")

    def __init__(self, *args, **kwargs):
        student = kwargs.pop('student')
        tutors = kwargs.pop('tutors')
        venues = kwargs.pop('venues')
        super().__init__(*args, **kwargs)
        self.fields['tutor'].label_from_instance = self.get_tutor_label

        # Manually populate some fields based on what the tutoring request specifies.
        self.fields['day'].queryset = student.availability.all()
        self.fields['venue'].choices = [
            (venue.id, venue.venue) for venue in venues if venue.venue != 'No Preference'
        ]
        self.fields['tutor'].queryset = tutors

    def get_tutor_label(self, obj):
        return f'{obj.username} - {obj.first_name} {obj.last_name}'
