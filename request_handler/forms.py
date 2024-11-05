import django.forms as forms
from .models import Request, Day, Modality


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