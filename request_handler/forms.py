import django.forms as forms
from django.utils import timezone
from datetime import date,timedelta,datetime
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Request, Day, Modality

""" Class representing a form to create a Request instance.

This class is used as the form displayed to au student user when they wish to make a request for tutoring. They can fill
in all the fields and a Request instance containing that information will be created and stored in the database.
"""
class RequestForm(forms.ModelForm):
    availability = forms.ModelMultipleChoiceField(
        queryset=Day.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    venue_preference = forms.ModelMultipleChoiceField( 
        queryset=Modality.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    USER_TERM_CHOICES = [('September','September - December'),('January','January - April'),('May','May - July')]
    term = forms.ChoiceField(choices=USER_TERM_CHOICES, label='Term')

    

    class Meta:
        model = Request
        fields = ['knowledge_area', 'term', 'frequency', 'duration', 'availability', 'venue_preference']

