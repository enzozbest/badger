import django.forms as forms
from .models import Request
class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['knowledge_area', 'term', 'frequency','duration']