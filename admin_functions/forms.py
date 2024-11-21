import django.forms as forms
from user_system.models import Day, User

class AllocationForm(forms.Form):
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

        self.fields['day'].queryset = student.availability.all()
        self.fields['venue'].choices = [
            (venue.id, venue.venue) for venue in venues
        ]
        self.fields['tutor'].queryset = tutors
