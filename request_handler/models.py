from django.core.exceptions import ValidationError
from django.db import models
from user_system.models import User, Day



""" Class representing a venue for tutoring sessions.

This Model is necessary for the ManyToMany relationships in Request to work, as they must be between model instances.
Modes are represented in the database as a string (In person, Online, No preference) and an automatically assigned id (primary key).
"""
class Venue(models.Model):
    venue = models.CharField(max_length=10)
    def __str__(self):
        return self.venue

""" Class representing a request for lessons from a student.

This Model represents a request made by a student for lessons. It contains all the necessary details for an admin to 
contact the student and formalise arrangements. These details include: the student's user information, which knowledge areas
they would like tutoring for, which days of the week they are available, their preferred mode of attendance, etc.
"""

class Request(models.Model):
    student = models.ForeignKey(User, default=None, null=True, on_delete=models.CASCADE, related_name='student')
    allocated = models.BooleanField(default=False, blank=True)
    allocated_string = 'No'
    tutor_name_string = '-'
    tutor = models.OneToOneField(User, default=None, null=True, on_delete=models.CASCADE, blank=True, related_name='tutor')
    knowledge_area = models.CharField(max_length=255, blank=False)
    venue_preference = models.ManyToManyField(Venue, blank=False, related_name='student_venue_preference')
    term = models.CharField(max_length=255)
    frequency = models.CharField(max_length=255)
    duration = models.CharField(max_length=255, blank=False)
    late = models.BooleanField(default=False, blank=False)
    is_recurring = models.BooleanField(default=False)
    day = models.ForeignKey(Day, null=True, blank=True, on_delete=models.SET_NULL, related_name='allocated_day')
    venue = models.ForeignKey(Venue, null=True, blank=True, on_delete=models.SET_NULL, related_name='allocated_venue')

    @property
    def student_email(self):
        return self.student.email if self.student else None

    @property
    def tutor_name(self):
        return self.tutor.first_name + " " + self.tutor.last_name if self.tutor else None

    def __str__(self):
        venue = "No venue preference set!"

        if self.pk and self.venue_preference.exists():
            preferences = self.venue_preference.all()
            venue = ', '.join(str(pref) for pref in preferences)

        self.allocated_string = 'No'
        if self.allocated:
            self.allocated_string = 'Yes'

        self.tutor_name_string = '-'
        if self.tutor:
            self.tutor_name_string = self.tutor_name

        return (f'Student: {self.student_email}'
                f'\n Knowledge Area: {self.knowledge_area}'
                f'\n Term: {self.term}'
                f'\n Frequency: {self.frequency}'
                f'\n Duration: {self.duration}'
                f'\n Venue Preference: {venue}'
                f'\n Allocated?: {self.allocated_string}'
                f'\n Tutor: {self.tutor_name_string}'
                f'\n Late: {self.late}'
                f'\n Recurring?: {self.is_recurring}'
                )

    def clean(self):
        super().clean()
        if self.pk and not self.venue_preference.exists():
            raise ValidationError({"venue_preference": "No venue preference set!"})
