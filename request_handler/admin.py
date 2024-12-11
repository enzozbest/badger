from django.contrib import admin
from .models import Request


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'tutor', 'knowledge_area','day', 'term', 'venue')