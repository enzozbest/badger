import datetime

from django.db import models

from request_handler.models import Venue
from user_system.models.day_model import Day
from user_system.models.user_model import User

""" Class representing individual lessons that have been booked following a tutor accepting the request.

This Model represents a booking accepted by the tutor. It contains all the necessary details to be displayed when a 
student or tutor wants to view their booked lessons.
"""

class Booking(models.Model):
    lesson_identifier = models.IntegerField(blank=False, null=False, default=-1)
    student = models.ForeignKey(User, default=None, null=True, on_delete=models.CASCADE, related_name='booking_student')
    tutor_name_string = '-'
    tutor = models.ForeignKey(User, default=None, null=True, on_delete=models.SET_NULL, blank=True,
                              related_name='booking_tutor')
    knowledge_area = models.CharField(max_length=255, blank=False)
    term = models.CharField(max_length=255, null=True)
    frequency = models.CharField(max_length=255, null=True, default="Weekly")
    duration = models.CharField(max_length=255, blank=False, default="1h")
    is_recurring = models.BooleanField(default=False)
    day = models.ForeignKey(Day, null=True, blank=True, on_delete=models.SET_NULL, related_name='booking_allocated_day')
    venue = models.ForeignKey(Venue, null=True, blank=True, on_delete=models.SET_NULL,
                              related_name='booking_allocated_venue')
    date = models.DateField(null=False, blank=False, default=datetime.date(1900, 1, 1))
    title = models.CharField(max_length=255, null=False, default="Tutor session")
    cancellation_requested = models.BooleanField(blank=False, default=False)

    def __str__(self):
        return f"{self.student} is taught by {self.tutor} in the term {self.term}."