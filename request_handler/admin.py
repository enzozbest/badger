from django.contrib import admin
from .models import Booking, Request

# Register your models here.

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'tutor', 'knowledge_area', 'day', 'term', 'venue')

@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'tutor', 'knowledge_area','day', 'term', 'venue')