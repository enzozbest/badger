import django.forms as forms
from datetime import timedelta,datetime

from .models import Request, Day, Venue

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
        queryset=Venue.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    USER_KNOWLEDGE_AREA_CHOICES = [('C++','C++'),('Scala','Scala'),('Python','Python'),('Java','Java'),
                                   ('Django','Django'),('JavaScript','JavaScript'),('Databases','Databases'),
                                   ('Robotics','Robotics'),('Internet Systems','Internet Systems')]
    knowledge_area = forms.ChoiceField(choices=USER_KNOWLEDGE_AREA_CHOICES, label='Knowledge Area')

    USER_TERM_CHOICES = [('September','September - December'),('January','January - April'),('May','May - July')]
    term = forms.ChoiceField(choices=USER_TERM_CHOICES, label='Term')

    USER_FREQUENCY_CHOICES = [('Weekly','Weekly'),('Biweekly','Biweekly'),('Fortnightly','Fortnightly')]
    frequency = forms.ChoiceField(choices=USER_FREQUENCY_CHOICES, label='Frequency')

    USER_DURATION_CHOICES = [('0.5','30 minutes'),('1','1 hour'),('1.5','1 hour 30 minutes'),('2','2 hours')]
    duration = forms.ChoiceField(choices=USER_DURATION_CHOICES, label='Duration')

    #Ensure that a warning is shown when a student tries to make a late request
    def is_late_request(self):
        term = self.cleaned_data.get('term')
        todayDate = datetime.today()
        term_one = datetime(datetime.today().year,9,1) #September of current year
        if todayDate.month >= 8:
            term_two = datetime(datetime.today().year+1,1,1) #January of following year
            term_three = datetime(datetime.today().year+1,5,1) #May of following year
        else:
            term_two = datetime(datetime.today().year,1,1) #January of current year
            term_three = datetime(datetime.today().year,5,1) #May of current year

        late = False
        if term and ((term == "September" and todayDate > term_one - timedelta(weeks=2)) or 
        (term == "January" and todayDate > term_two - timedelta(weeks=2)) or 
        (term == "May" and todayDate > term_three - timedelta(weeks=2))):
            late = True

        return late
    

    class Meta:
        model = Request
        fields = ['knowledge_area', 'term', 'frequency', 'duration', 'availability', 'venue_preference']

