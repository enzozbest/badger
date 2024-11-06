import django.forms as forms
from .models import Request, Day, Modality

""" Class representing a form to create a Request instance.

This class is used as the form displayed to au student user when they wish to make a request for tutoring. They can fill
in all the fields and a Request instance containing that information will be created and stored in the database.
"""
class RequestForm(forms.ModelForm):

    available_days = forms.ModelMultipleChoiceField(
        queryset=Day.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    mode_preference = forms.ModelMultipleChoiceField(
        queryset=Modality.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = Request
        fields = ['knowledge_area', 'term', 'frequency','duration', 'available_days', 'mode_preference']