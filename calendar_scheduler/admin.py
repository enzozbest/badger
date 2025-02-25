from django.contrib import admin
from .models import Booking

# Register your models here.
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'lesson_identifier', 'student', 'tutor', 'knowledge_area', 'day', 'term', 'venue', 'date', 'is_recurring', 'frequency')