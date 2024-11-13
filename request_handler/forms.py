import django.forms as forms
from datetime import timedelta,datetime

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

    #Ensure that a warning is shown when a student tries to make a late request
    def is_late_request(self):
        term = self.cleaned_data.get('term')
        todayDate = datetime.today()
        term_one = datetime(datetime.today().year,9,1) #September of current year
        if todayDate.month >= 8:
            term_two = datetime(datetime.today().year+1,1,1) #January of following year
            term_three = datetime(datetime.today().year+1,5,1) #May of current/following year
        else:
            term_two = datetime(datetime.today().year,1,1) #January of following year
            term_three = datetime(datetime.today().year,5,1) #May of current/following year

        if term:
            return ((term == "September" and todayDate > term_one - timedelta(weeks=2)) or 
            (term == "January" and todayDate > term_two - timedelta(weeks=2)) or 
            (term == "May" and todayDate > term_three - timedelta(weeks=2)))
        return term
    

    class Meta:
        model = Request
        fields = ['knowledge_area', 'term', 'frequency', 'duration', 'availability', 'venue_preference']

