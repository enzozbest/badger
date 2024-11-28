from django.db import models
from user_system.models import User,Day
import datetime

""" Class representing a venue for tutoring sessions.

This Model is necessary for the ManyToMany relationships in Request to work, as they must be between model instances.
Modes are represented in the database as a string (In person, Online, No preference) and an automatically assigned id (primary key).
"""
class Venue(models.Model):
    venue = models.CharField(max_length=10)
    def __str__(self):
        return self.venue

""" Class representing individual lessons that have been booked following a tutor accepting the request.

This Model represents a booking accepted by the tutor. It contains all the necessary details to be displayed when a 
student or tutor wants to view their booked lessons.
"""
class Booking(models.Model):
    student = models.ForeignKey(User, default=None, null=True, on_delete=models.CASCADE, related_name='booking_student')
    tutor_name_string = '-'
    tutor = models.ForeignKey(User, default=None, null=True, on_delete=models.SET_NULL, blank=True,
                              related_name='booking_tutor')
    knowledge_area = models.CharField(max_length=255, blank=False)
    venue_preference = models.ManyToManyField(Venue, blank=False, related_name='booking_student_venue_preference')
    term = models.CharField(max_length=255, null=True)
    frequency = models.CharField(max_length=255, null=True, default="Weekly")
    duration = models.CharField(max_length=255, blank=False, default="1h")
    is_recurring = models.BooleanField(default=False)
    day = models.ForeignKey(Day, null=True, blank=True, on_delete=models.SET_NULL, related_name='booking_allocated_day')
    venue = models.ForeignKey(Venue, null=True, blank=True, on_delete=models.SET_NULL, related_name='booking_allocated_venue')
    date = models.DateField(null=False, blank=False, default=datetime.date(1900, 1, 1)) #Could be changed to a datetimefield if we want to include time availability


    def __str__(self):
        return f"{self.student} -> {self.tutor} ({self.day}) {self.date}"