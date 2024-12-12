from django.contrib import admin
from .models.request_model import Request


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'tutor', 'knowledge_area', 'day', 'term', 'venue')
