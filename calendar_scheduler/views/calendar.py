from calendar import Calendar
from datetime import date, datetime, timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views import View
from schedule.models import Calendar

from calendar_scheduler.models import Booking
from user_system.models.user_model import User

def get_month_days(year: int, month: int):
    """ Returns all the days for a particular month as a list, per the year and month parameters."""

    # Get the first day of the month and the total days in the month
    first_day = datetime(year, month, 1)
    last_day = datetime(year, month + 1, 1) if month != 12 else datetime(year + 1, 1, 1)

    # Find the weekday of the first day (0=Monday, 6=Sunday)
    first_weekday = first_day.weekday()

    # Get the total number of days in the month
    total_days = (last_day - first_day).days

    month_days = []
    week = [''] * first_weekday  # Start with empty days until the first day

    # Fill the week with the actual days
    for day in range(1, total_days + 1):
        week.append(day)
        if len(week) == 7:  # If the week is full, add it to month_days
            month_days.append(week)
            week = []

    # If the week has any days leftover (less than 7), add them as well
    if week:
        month_days.append(week)

    return month_days

def get_month_name(month_number: int):
    """ Returns the name of the month corresponding to the passed number e.g. get_month_name(4) returns April."""
    MONTHS = {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December"
    }
    return MONTHS.get(month_number, "Invalid month")

def get_week_days():
    """ Returns the week days of the current week """
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    return [start_of_week + timedelta(days=i) for i in range(7)]

def compute_months(month:int, year:int):
    """ Calculates the previous and next months and years for the calendar display
    This allows users to click between each month on the calendar
    """
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

    return [prev_month, prev_year, next_month, next_year], month, year

def produce_month_events(request: HttpRequest, year: int, month: int, user_for_calendar: User):
    """ Collates all the events for the given month into an events list."""
    events = []
    for day in range(1, 31):
        try:
            selected_date = date(year, month, day)
            match request.user.user_type:
                case 'Student' if Booking.objects.filter(student=request.user, date=selected_date).exists():
                    events.append(Booking.objects.filter(student=request.user, date=selected_date))
                case 'Tutor' if Booking.objects.filter(tutor=request.user, date=selected_date).exists():
                    events.append(Booking.objects.filter(tutor=request.user, date=selected_date))
                case 'Admin' if user_for_calendar and user_for_calendar.user_type == 'Student':
                    newEvent = Booking.objects.filter(student=user_for_calendar, date=selected_date)
                    if newEvent.exists():
                        events.append(newEvent)
                case 'Admin' if user_for_calendar and user_for_calendar.user_type == 'Tutor':
                    newEvent = Booking.objects.filter(tutor=user_for_calendar, date=selected_date)
                    if newEvent.exists():
                        events.append(newEvent)
                case 'Admin' if not user_for_calendar: # If no specific user is selected, admin sees all events
                    newEvent = Booking.objects.filter(date=selected_date)
                    if newEvent.exists():
                        events.append(newEvent)
        except ValueError:
            break
    return events

def retrieve_calendar_events(calendar, request, user_for_calendar=None):
    """ Retrieves all relevant tutoring sessions for a particular day 
    The day is associated with the day attribute of the request parameter
    The calendar parameter is a Calendar object from django-scheduler/schedule
    """

    # Get today's date for the default display
    today = datetime.today()
    year = int(request.GET.get("year", today.year))
    month = int(request.GET.get("month", today.month))

    prev_next_dates, month, year = compute_months(month, year)

    month_days = get_month_days(year, month)

    events = produce_month_events(request, year, month, user_for_calendar)
    
    return {
        "calendar": calendar,
        "year": year,
        "month": month,
        "month_name": get_month_name(month),
        "month_days": month_days,
        "events": events,
        "prev_month": prev_next_dates[0],
        "prev_year": prev_next_dates[1],
        "next_month": prev_next_dates[2],
        "next_year": prev_next_dates[3],
    }

class BaseCalendarView(LoginRequiredMixin, View):
    calendar_slug = None
    template_name = None
    user_type = None
    admin_template_name = None

    def get(self, request: HttpRequest, pk: int = None) -> HttpResponse:
        if request.user.user_type != self.user_type and not request.user.is_admin:
            return render(request, 'permission_denied.html', status=401)
        
        user_for_calendar = None
        if request.user.is_admin and pk:
            user_for_calendar = get_object_or_404(User, pk=pk)
            if user_for_calendar.user_type != self.user_type:
                raise ValueError(f"Unexpected user type. Only {self.user_type} is expected for this calendar.")
            else:
                self.template_name = self.admin_template_name
        try:
            calendar = Calendar.objects.get(slug=self.calendar_slug)
            data = retrieve_calendar_events(calendar, request, user_for_calendar)
            return render(request, self.template_name, data)
        except Calendar.DoesNotExist:
            return render(request, 'dashboard.html', status=404)
        
    
class TutorCalendarView(BaseCalendarView):
    calendar_slug = 'tutor'
    template_name = 'tutor_calendar.html'
    user_type = 'Tutor'
    admin_template_name = 'admin_tutor_calendar.html'

class StudentCalendarView(BaseCalendarView):
    calendar_slug = 'student'
    template_name = 'student_calendar.html'
    user_type = 'Student'
    admin_template_name = 'admin_student_calendar.html'