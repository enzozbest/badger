from zoneinfo import available_timezones

from django.db import models
from tutorials.models import User
# Create your models here.

class Day(models.Model):
    day = models.CharField(max_length=10)
    def __str__(self):
        return self.day

class Modality(models.Model):
    mode = models.CharField(max_length=10)
    def __str__(self):
        return self.mode

class Request(models.Model):
    student = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    knowledge_area = models.CharField(max_length=255,blank=False) #Allow one for now, extend later.
    availability = models.ManyToManyField(Day, blank=False)
    venue_preference = models.ManyToManyField(Modality, blank=False)
    term = models.CharField(max_length=255)
    frequency = models.CharField(max_length=255)
    duration = models.CharField(max_length=255, blank=False)

    @property
    def student_email(self):
        return self.student.email

    def __str__(self):
        if self.pk and self.availability.exists():
            available = ', '.join(str(day) for day in self.availability.all())
        else:
            available = 'No availability set!'

        return (f'Student: {self.student_email}'
                f'\n Knowledge_area: {self.knowledge_area}'
                f'\n Availability: {available}'
                f'\n Term: {self.term}'
                f'\n Frequency: {self.frequency}'
                f'\n Duration: {self.duration}')
