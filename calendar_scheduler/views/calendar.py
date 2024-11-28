from calendar import Calendar

from django.shortcuts import render, redirect
from calendar_scheduler.models import Booking
from schedule.models import Calendar, Event
from datetime import datetime,date,timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import HttpRequest, HttpResponse

''' Returns all the days for a particular month as a list, per the year and month parameters '''
def get_month_days(year, month):
    # Get the first day of the month and the total days in the month
    first_day = datetime(year, month, 1)
    last_day = datetime(year, month + 1, 1) if month != 12 else datetime(year + 1, 1, 1)
    
    # Find the weekday of the first day (0=Monday, 6=Sunday)
    first_weekday = first_day.weekday()
    
    # Get the total number of days in the month
    total_days = (last_day - first_day).days
    
    # Prepare a list to hold weeks (each week is a list of days)
    month_days = []
    week = [''] * first_weekday  # Start with empty days until the first day
    
    # Fill the week with the actual days
    for day in range(1, total_days + 1):
        week.append(day)
        if len(week) == 7:  # If the week is full, add it to month_days
            month_days.append(week)
            week = []
    
    # If the week has leftover days (less than 7), add them as well
    if week:
        month_days.append(week)
    
    return month_days   

def get_week_days():
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    return [start_of_week + timedelta(days=i) for i in range(7)]
        
''' Retrieves all relevant tutoring sessions for a particular day 

The day is associated with the day attribute of the request parameter

The calendar parameter is a Calendar object from django-scheduler/schedule
'''
def retrieve_calendar_events(calendar,request):
    # Get today's date for the default display
    today = datetime.today()
    year = int(request.GET.get("year", today.year))
    month = int(request.GET.get("month", today.month))
    day = int(request.GET.get("day", 0))  # Default to 0 if no day is provided

    # Ensure month/year remain valid
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1

    # Compute previous and next month/year
    prev_month = month - 1 if month > 1 else 12
    prev_year = year - 1 if month == 1 else year
    next_month = month + 1 if month < 12 else 1
    next_year = year + 1 if month == 12 else year
    
    month_days = get_month_days(year,month)
    events = []

    if day:
        selected_date = date(year, month, day)
        if request.user.user_type == 'Student':
            events = Booking.objects.filter(student=request.user, date=selected_date)
        elif request.user.user_type == 'Tutor':
            events = Booking.objects.filter(tutor=request.user, date=selected_date)
    
    return {
            "calendar": calendar,
            "year": year,
            "month": month,
            "month_days": month_days,
            "events": events,
            "day": day,
            "prev_month": prev_month,
            "prev_year": prev_year,
            "next_month": next_month,
            "next_year": next_year,
        }

class TutorCalendarView(LoginRequiredMixin,View):
    def get(self, request: HttpRequest) -> HttpResponse:
        if not request.user.is_tutor:
            return render(request, 'permission_denied.html', status=401)
        try:
            calendar = Calendar.objects.get(slug='tutor')
            data = retrieve_calendar_events(calendar,request)
            return render( request,'tutor_calendar.html', data)
        except Calendar.DoesNotExist:
            return render(request, 'dashboard',status=404)
        
class StudentCalendarView(LoginRequiredMixin,View):
    def get(self, request: HttpRequest) -> HttpResponse:
        if not request.user.is_student:
            return render(request, 'permission_denied.html', status=401)
        try:
            calendar = Calendar.objects.get(slug='tutor')
            data = retrieve_calendar_events(calendar,request)
            return render( request,'student_calendar.html', data)
        except Calendar.DoesNotExist:
            return render(request, 'dashboard',status=404)
