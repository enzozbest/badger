from datetime import datetime, timedelta

import django.forms as forms

from user_system.forms.knowledge_area_form import get_knowledge_areas
from .models import Venue
from .models.request_model import Request


class RequestForm(forms.ModelForm):
    """ Class representing a form to create a tutoring Request instance.

    This class is used as the form displayed to a student user when they wish to make a request for tutoring. They can fill
    in all the fields and a Request instance containing that information will be created and stored in the database.
    """
    def __init__(self, *args, **kwargs):
        super(RequestForm, self).__init__(*args, **kwargs)
        self.fields['is_recurring'].label = 'Would you like your sessions to continue across the year?'

    venue_preference = forms.ModelMultipleChoiceField(
        queryset=Venue.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    USER_KNOWLEDGE_AREA_CHOICES = get_knowledge_areas()
    knowledge_area = forms.ChoiceField(choices=USER_KNOWLEDGE_AREA_CHOICES, label='Knowledge Area')

    USER_TERM_CHOICES = [('September', 'September - December'), ('January', 'January - April'), ('May', 'May - July')]
    term = forms.ChoiceField(choices=USER_TERM_CHOICES, label='Term')

    USER_FREQUENCY_CHOICES = [('Weekly', 'Weekly'), ('Biweekly', 'Biweekly'), ('Fortnightly', 'Fortnightly')]
    frequency = forms.ChoiceField(choices=USER_FREQUENCY_CHOICES, label='Frequency')

    USER_DURATION_CHOICES = [('0.5', '30 minutes'), ('1', '1 hour'), ('1.5', '1 hour 30 minutes'), ('2', '2 hours')]
    duration = forms.ChoiceField(choices=USER_DURATION_CHOICES, label='Duration')

    def is_late_request(self):
        """Ensure that a warning is shown when a student tries to make a late request."""
        term = self.cleaned_data.get('term')
        today_date = datetime.today()
        term_one, term_two, term_three = get_term_dates(today_date)

        return term and ((term == "September" and today_date > term_one - timedelta(weeks=2)) or
                         (term == "January" and today_date > term_two - timedelta(weeks=2)) or
                         (term == "May" and today_date > term_three - timedelta(weeks=2)))
    

    class Meta:
        model = Request
        fields = ['knowledge_area', 'term', 'frequency', 'duration', 'venue_preference', 'is_recurring']


def get_term_dates(today):
    term_one = datetime(today.year, 9, 1)  # September of current year
    if today.month >= 8:
        term_two = datetime(today.year + 1, 1, 1)  # January of following year
        term_three = datetime(today.year + 1, 5, 1)  # May of following year
    else:
        term_two = datetime(today.year, 1, 1)  # January of current year
        term_three = datetime(today.year, 5, 1)  # May of current year
    return term_one, term_two, term_three


class RejectRequestForm(forms.Form):
    """Class representing a form for when an admin rejects a request and provides a reason."""

    reason = forms.CharField(widget=forms.Textarea, label='Reason for rejection:')
