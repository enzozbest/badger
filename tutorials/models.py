from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar

class User(AbstractUser):
    """Model used for user authentication, and team member related information."""
    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[RegexValidator(
            regex=r'^@\w{3,}$',
            message='Username must consist of @ followed by at least three alphanumericals'
        )]
    )

    ACCOUNT_TYPE_STUDENT = 'Student'
    ACCOUNT_TYPE_TUTOR = 'Tutor'
    ACCOUNT_TYPE_ADMIN = 'Admin'
    CHOICES = [(ACCOUNT_TYPE_STUDENT, 'Student'), (ACCOUNT_TYPE_TUTOR, 'Tutor'), (ACCOUNT_TYPE_ADMIN, 'Admin')]
    user_type = models.CharField(max_length=20, blank=False, null=False, choices=CHOICES)
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)

    def __str__(self):
        return (f'Username: {self.username} \n'
                f'First Name: {self.first_name} \n'
                f'Last Name: {self.last_name} \n'
                f'User Type: {self.user_type} \n'
                f'Email Address: {self.email}'
                )

    models.pk = email

    @property
    def is_tutor(self): # Used in views.py to add knowledge areas
        return self.user_type == self.ACCOUNT_TYPE_TUTOR


    class Meta:
        """Model options."""

        ordering = ['last_name', 'first_name']

    def full_name(self):
        """Return a string containing the user's full name."""

        return f'{self.first_name} {self.last_name}'

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""

        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""

        return self.gravatar(size=60)


class KnowledgeArea(models.Model): # check if the line below creates a new table?
    user = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_tutor': True}) # maybe change to 'user_type': 'tutor'
    subject = models.CharField(max_length=100)

    def __str__(self):
        return self.subject
