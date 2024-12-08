from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from libgravatar import Gravatar


class Day(models.Model):
    """ Class representing a day of the week

    This Model is necessary for the ManyToMany relationships in Request to work, as they must be between model instances.
    Days are represented in the database as a string (their name) and an automatically assigned id (primary key).
    """

    day = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.day


class User(AbstractUser):
    """Model used for user authentication, and team member related information."""
    ACCOUNT_TYPE_STUDENT = 'Student'
    ACCOUNT_TYPE_TUTOR = 'Tutor'
    ACCOUNT_TYPE_ADMIN = 'Admin'

    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[RegexValidator(
            regex=r'^@\w{3,}$',
            message='Username must consist of @ followed by at least three alphanumericals'
        )]
    )
    CHOICES = [(ACCOUNT_TYPE_STUDENT, 'Student'), (ACCOUNT_TYPE_TUTOR, 'Tutor'), (ACCOUNT_TYPE_ADMIN, 'Admin')]
    user_type = models.CharField(max_length=20, blank=False, null=False, choices=CHOICES)

    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)
    availability = models.ManyToManyField(Day, blank=False, default=None)
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, default=0.00,
                                      help_text="Enter your hourly rate in GBP.")
    student_max_rate = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, default=0.00,
                                           help_text="Enter the maximum hourly rate you are willing to pay, in GBP.")
    models.pk = email

    @property
    def is_tutor(self):
        return self.user_type == self.ACCOUNT_TYPE_TUTOR

    @property
    def is_admin(self):
        return self.user_type == self.ACCOUNT_TYPE_ADMIN

    @property
    def is_student(self):
        return self.user_type == self.ACCOUNT_TYPE_STUDENT

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return (f'Username: {self.username} \n'
                f'First Name: {self.first_name} \n'
                f'Last Name: {self.last_name} \n'
                f'User Type: {self.user_type} \n'
                f'Email Address: {self.email}'
                )

    class Meta:
        """Model options."""

        ordering = ['last_name', 'first_name']

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        return self.gravatar(size=60)


class KnowledgeArea(models.Model):
    """Model to associate tutors to their knowledge areas."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_tutor': True})
    subject = models.CharField(max_length=30)

    def __str__(self):
        return self.subject
