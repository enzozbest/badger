"""Forms for the user_system app."""
from django import forms
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from .models import User, KnowledgeArea, Day


class LogInForm(forms.Form):
    """Form enabling registered users to log in."""

    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

    def get_user(self):
        """Returns authenticated user if possible."""

        user = None
        if self.is_valid():
            username = self.cleaned_data.get('username')
            password = self.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
        return user


class UserForm(forms.ModelForm):
    """Form to update user profiles."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_type'].label = 'Account Type'
        self.fields['user_type'].disabled = True
        self.fields['user_type'].required = False
        hourly_rate = forms.DecimalField(max_digits=6, decimal_places=2)

        if 'instance' in kwargs:
            self.fields['user_type'].initial = kwargs['instance'].user_type

        # Display hourly rate only for tutors
        if self.instance.user_type != User.ACCOUNT_TYPE_TUTOR:
            self.fields.pop('hourly_rate', None)
        else:
            self.fields['hourly_rate'].label = 'Hourly Rate (in £)'
            self.fields['hourly_rate'].widget.attrs['placeholder'] = 'Enter your hourly rate e.g., 22.50'
            self.fields['hourly_rate'].required = False

    # Validates hourly rate to make sure it is 0 or positive
    def clean_hourly_rate(self):
        hourly_rate = self.cleaned_data.get('hourly_rate')
        if hourly_rate is not None and hourly_rate <= 0:
            raise forms.ValidationError('Hourly rate must be a positive number!')
        return hourly_rate

    def clean_username(self):
        username = self.cleaned_data['username']
        # Check if the username is already in use by another user
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("User with this username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        # Check if the email is already in use by another user
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("User with this email address already exists.")
        return email

    availability = forms.ModelMultipleChoiceField(
        label='Availability',
        queryset=Day.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False
    )

    class Meta:
        """Form options."""
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'user_type', 'hourly_rate', 'availability']

class NewPasswordMixin(forms.Form):
    """Form mixing for new_password and password_confirmation fields."""

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
            )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Form mixing for new_password and password_confirmation fields."""
        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')


class PasswordForm(NewPasswordMixin):
    """Form enabling users to change their password."""

    password = forms.CharField(label='Current password', widget=forms.PasswordInput())

    def __init__(self, user=None, **kwargs):
        """Construct new form instance with a user instance."""
        
        super().__init__(**kwargs)
        self.user = user

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        password = self.cleaned_data.get('password')
        if self.user is not None:
            user = authenticate(username=self.user.username, password=password)
        else:
            user = None
        if user is None:
            self.add_error('password', "Password is invalid")

    def save(self):
        """Save the user's new password."""

        new_password = self.cleaned_data['new_password']
        if self.user is not None:
            self.user.set_password(new_password)
            self.user.save()
        return self.user


class SignUpForm(NewPasswordMixin, forms.ModelForm):
    """Form enabling unregistered users to sign up."""
    USER_SIGNUP_CHOICES = [(User.ACCOUNT_TYPE_TUTOR, 'Tutor'), (User.ACCOUNT_TYPE_STUDENT, 'Student')]
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

def get_knowledge_areas():
    return [
        ('C++', 'C++'),
        ('Scala', 'Scala'),
        ('Python', 'Python'),
        ('Java', 'Java'),
        ('Django', 'Django'),
        ('JavaScript', 'JavaScript'),
        ('Databases', 'Databases'),
        ('Robotics', 'Robotics'),
        ('Internet Systems', 'Internet Systems'),
    ]

class KnowledgeAreaForm(forms.ModelForm):
    """Form to set knowledge areas."""
    class Meta:
        model = KnowledgeArea
        fields = ['subject']

    subject = forms.ChoiceField(choices=get_knowledge_areas())


