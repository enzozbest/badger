import django.forms as forms

from user_system.models import Day, User


class AllocationForm(forms.Form):
    """Class to represent the form which Admins use to allocate a student's tutoring request to a suitable tutor."""

    day1 = forms.ModelChoiceField(
        label='Choose a day for the allocation',
        queryset=Day.objects.none(),
    )

    day2 = forms.ModelChoiceField(
        label='Choose a second day for the allocation',
        queryset=Day.objects.none(),
        required=False,
    )

    venue = forms.ChoiceField(choices=[], label="Choose a Venue", required=False)
    tutor = forms.ModelChoiceField(queryset=User.objects.none(), label="Choose a Tutor", required=False)

    def __init__(self, *args, **kwargs):
        student = kwargs.pop('student')
        tutors = kwargs.pop('tutors', None)
        venues = kwargs.pop('venues')
        freq = kwargs.pop('frequency', None)
        super().__init__(*args, **kwargs)
        # Manually populate some fields based on what the tutoring request specifies
        self.fields['day1'].widget = forms.Select(attrs={'onchange': 'this.form.submit()'},
                                                  choices=[(day.id, day.day) for day in student.availability.all()])

        # Determine if Tutor selection should be visible
        if tutors:
            self.fields['tutor'].widget = forms.Select()
            self.fields['tutor'].choices = [(tutor.id, self.get_tutor_label(tutor)) for tutor in tutors]
            self.fields['tutor'].label_from_instance = self.get_tutor_label
        else:
            self.fields['tutor'].widget = forms.HiddenInput()

        # Determine if second day should be visible
        if freq == 'Biweekly' and self.data.get('day1'):
            try:
                selected_day = int(self.data.get('day1'))
                self.fields['day2'].widget = forms.Select(attrs={'onchange': 'this.form.submit()'})
                self.fields['day2'].queryset = student.availability.all().exclude(id=selected_day)
            except (ValueError, Day.DoesNotExist):
                self.fields['day2'].queryset = student.availability.all()
        else:
            self.fields['day2'].queryset = student.availability.none()
            self.fields['day2'].widget = forms.HiddenInput()

        # Display Venue Choices only after day selection:
        if not self.data.get('day1'):
            self.fields['venue'].widget = forms.HiddenInput()

        if freq == 'Biweekly' and not self.data.get('day2'):
            self.fields['venue'].widget = forms.HiddenInput()
        else:
            self.fields['venue'].widget = forms.Select()
            self.fields['venue'].choices = [
                (venue.id, venue.venue) for venue in venues if venue.venue != 'No Preference'
            ]

    def get_tutor_label(self, obj):
        return f'{obj.username} - {obj.first_name} {obj.last_name}'
