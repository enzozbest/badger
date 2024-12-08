from django import forms

from user_system.models import Day, User


class UserForm(forms.ModelForm):
    """Form to update user profiles."""

    availability = forms.ModelMultipleChoiceField(
        label='Availability',
        queryset=Day.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_type'].label = 'Account Type'
        self.fields['user_type'].disabled = True
        self.fields['user_type'].required = False

        if 'instance' in kwargs:
            self.fields['user_type'].initial = kwargs['instance'].user_type

        self._display_fields()

    # Validates hourly rate to make sure it is 0 or positive
    def clean_hourly_rate(self):
        hourly_rate = self.cleaned_data.get('hourly_rate')
        if hourly_rate is not None and hourly_rate <= 0:
            raise forms.ValidationError('Hourly rate must be a positive number!')
        return hourly_rate

    # Validates the maximum hourly rate set by a student to make sure it is 0 or positive
    def clean_student_max_rate(self):
        student_max_rate = self.cleaned_data.get('student_max_rate')
        if student_max_rate is not None and student_max_rate <= 0:
            raise forms.ValidationError('Student max hourly rate must be a positive number!')
        return student_max_rate

    # Check if the username is already in use by another user
    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("User with this username already exists.")
        return username

    # Check if the email is already in use by another user
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("User with this email address already exists.")
        return email

    def clean(self):
        """Form mixing for new_password and password_confirmation fields."""
        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')

    class Meta:
        """Form options."""
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'user_type', 'hourly_rate', 'student_max_rate',
                  'availability']

    # --HELPERS-- #
    # Display a field in the form only if the user is of the required type.
    def _display_field(self, field_name, field_label, placeholder, user_type):
        if self.instance.user_type != user_type:
            self.fields.pop(field_name, None)
            return

        self.fields[field_name].label = field_label
        self.fields[field_name].widget.attrs['placeholder'] = placeholder
        self.fields[field_name].required = False

    def _display_fields(self):
        self._display_field('hourly_rate', 'Hourly Rate (in £)', 'Enter your hourly rate e.g., 22.50',
                            User.ACCOUNT_TYPE_TUTOR)
        self._display_field('student_max_rate', 'Maximum Hourly Rate (in £)', 'Enter your the maximum hourly '
                                                                              'rate you are willing to pay, e.g., 22.50',
                            User.ACCOUNT_TYPE_STUDENT)
