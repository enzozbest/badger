from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import QuerySet

from invoicer.models import Invoice
from request_handler.models.venue_model import Venue
from user_system.models.day_model import Day
from user_system.models.user_model import User


class Request(models.Model):
    """ Class representing a request for lessons from a student.

    This Model represents a request made by a student for lessons. It contains all the necessary details for an admin to
    contact the student and formalise arrangements. These details include: the student's user information, which knowledge areas
    they would like tutoring for, which days of the week they are available, their preferred mode of attendance, etc.
    """

    student = models.ForeignKey(User, default=None, null=True, on_delete=models.CASCADE, related_name='student')
    allocated = models.BooleanField(default=False, blank=True)
    allocated_string = 'No'
    tutor_name_string = '-'
    tutor = models.ForeignKey(User, default=None, null=True, on_delete=models.SET_NULL, blank=True,
                              related_name='tutor')
    knowledge_area = models.CharField(max_length=255, blank=False)
    venue_preference = models.ManyToManyField(Venue, blank=False, related_name='student_venue_preference')
    term = models.CharField(max_length=255)
    frequency = models.CharField(max_length=255)
    duration = models.CharField(max_length=255, blank=False)
    late = models.BooleanField(default=False, blank=False)
    is_recurring = models.BooleanField(default=False)
    day = models.ForeignKey(Day, null=True, blank=True, on_delete=models.SET_NULL, related_name='allocated_day')
    day2 = models.ForeignKey(Day, null=True, blank=True, on_delete=models.SET_NULL, related_name='allocated_day2')
    venue = models.ForeignKey(Venue, null=True, blank=True, on_delete=models.SET_NULL, related_name='allocated_venue')
    invoice = models.ForeignKey(Invoice, null=True, blank=True, on_delete=models.SET_NULL,
                                related_name='request_invoice')
    rejected_request = models.BooleanField(default=False, null=True)
    rejection_reason = models.TextField(blank=True, null=True)

    @property
    def student_email(self):
        return self.student.email if self.student else None

    @property
    def tutor_name(self):
        return self.tutor.full_name if self.tutor else None

    def __str__(self):
        self.allocated_string = self.get_allocation_str()
        return (f'Student: {self.student_email}'
                f'\n Knowledge Area: {self.knowledge_area}'
                f'\n Term: {self.term}'
                f'\n Frequency: {self.frequency}'
                f'\n Duration: {self.duration}'
                f'\n Venue Preference: {get_venue_preference_str(self.pk, self.venue_preference)}'
                f'\n Allocated?: {self.allocated_string}'
                f'\n Tutor: {self.tutor_name if self.tutor else "-"}'
                f'\n Late: {self.late}'
                f'\n Recurring?: {self.is_recurring}'
                )

    def get_allocation_str(self):
        if self.allocated:
            return 'Yes'
        return 'No'

    def clean(self):
        super().clean()
        if self.pk and not self.venue_preference.exists():
            raise ValidationError({"venue_preference": "No venue preference set!"})


def get_venue_preference_str(pk, venue_preference: QuerySet):
    if pk and venue_preference.exists():
        preferences = venue_preference.all()
        return ', '.join(str(pref) for pref in preferences)
    return 'No venue preference set!'
