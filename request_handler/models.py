from django.core.exceptions import ValidationError
from django.db import models
from tutorials.models import User

""" Class representing a day of the week

This Model is necessary for the ManyToMany relationships in Request to work, as they must be between model instances.
Days are represented in the database as a string (their name) and an automatically assigned id (primary key).
"""
class Day(models.Model):
    day = models.CharField(max_length=10)
    def __str__(self):
        return self.day

""" Class representing a mode of attendance

This Model is necessary for the ManyToMany relationships in Request to work, as they must be between model instances.
Modes are represented in the database as a string (In person, Online, No preference) and an automatically assigned id (primary key).
"""
class Modality(models.Model):
    mode = models.CharField(max_length=10)
    def __str__(self):
        return self.mode

""" Class representing a request for lessons from a student.

This Model represents a request made by a student for lessons. It contains all the necessary details for an admin to 
contact the student and formalise arrangements. These details include: the student's user information, which knowledge areas
they would like tutoring for, which days of the week they are available, their preferred mode of attendance, etc.
"""

class Request(models.Model):
    student = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    knowledge_area = models.CharField(max_length=255, blank=False)
    availability = models.ManyToManyField(Day, blank=False)
    venue_preference = models.ManyToManyField(Modality, blank=False)
    term = models.CharField(max_length=255)
    frequency = models.CharField(max_length=255)
    duration = models.CharField(max_length=255, blank=False)

    @property
    def student_email(self):
        return self.student.email if self.student else None

    def __str__(self):
        available = 'No availability set!'
        if self.pk and self.availability.exists():
            available_days = self.availability.all()
            if available_days.exists():
                available = ', '.join(str(day) for day in available_days)

        return (f'Student: {self.student_email}'
                f'\n Knowledge_area: {self.knowledge_area}'
                f'\n Availability: {available}'
                f'\n Term: {self.term}'
                f'\n Frequency: {self.frequency}'
                f'\n Duration: {self.duration}')

    def clean(self):
        super().clean()
        if self.pk and not self.availability.exists():
            raise ValidationError({"availability": "No availability set!"})
        if self.pk and not self.venue_preference.exists():
            raise ValidationError({"venue_preference": "No venue preference set!"})
