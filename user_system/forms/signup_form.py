from django import forms

from user_system.forms import NewPasswordMixin
from user_system.models.day_model import Day
from user_system.models.user_model import User

USER_SIGNUP_CHOICES = [(User.ACCOUNT_TYPE_TUTOR, 'Tutor'), (User.ACCOUNT_TYPE_STUDENT, 'Student')]


class SignUpForm(NewPasswordMixin, forms.ModelForm):
    """Form enabling unregistered users to sign up."""

    user_type = forms.ChoiceField(choices=USER_SIGNUP_CHOICES, label='Account Type')
    availability = forms.ModelMultipleChoiceField(
        label='Availability',
        queryset=Day.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False
    )

    class Meta:
        """Form options."""
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'user_type', 'availability']

    def save(self):
        """Create a new user."""

        super().save(commit=False)
        user = User.objects.create_user(
            self.cleaned_data.get('username'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('new_password'),
            user_type=self.cleaned_data.get('user_type'),
        )
        
        return user
