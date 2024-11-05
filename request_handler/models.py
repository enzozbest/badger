from django.db import models
from tutorials.models import User
# Create your models here.

class Request(models.Model):
  #  student_email = models.ForeignKey(User, on_delete=models.CASCADE) Link request to a Student
    knowledge_area = models.CharField(max_length=255,blank=False) #Allow one for now, extend later.
    #availability #JSON list
    term = models.CharField(max_length=255)
    frequency = models.CharField(max_length=255)
    duration = models.CharField(max_length=255, blank=False)

    def __str__(self):
        return (f'Student: {self.student_email}'
                f'\n Knowledge_area: {self.knowledge_area}'
                f'\n Term: {self.term}'
                f'\n Frequency: {self.frequency}'
                f'\n Duration: {self.duration}')