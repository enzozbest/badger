from calendar import Calendar

from django.shortcuts import render
from request_handler.models import Booking
from schedule.models import Calendar, Event
from datetime import datetime,date,timedelta
from django.contrib.auth.decorators import login_required

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


def tutor_calendar(request):
    if not request.user.is_tutor:
        return render(request, '403.html') # Make this file
    bookings = Booking.objects.filter(tutor=request.user)

    week_days = get_week_days()
    calendar_data = {day: [] for day in week_days}
    for booking in bookings:
        for day in week_days:
            print(booking.day)
            print(booking.day.day)
            print(day.strftime("%A"))

            if booking.day and booking.day.day == day.strftime('%A'): ### GIVES MONDAY MONDAY SUNDAY ###
                calendar_data[day].append(booking)
            else:
                print("NOT EQUAL DAYS") ##### THE DAYS ARE NOT EQUAL SO THIS IS NOT WORKING #######

    return render(request, 'tutor_calendar.html', {'week_days': week_days, 'calendar_data': calendar_data})

@login_required
def student_calendar(request):
    calendar_slug = "student"
    try:
        calendar = Calendar.objects.get(slug=calendar_slug)
    except Calendar.DoesNotExist:
        return render(request, "calendar/error.html", {"message": "Calendar not found."}) #Still need to make this page

    # Get today's date for the default display
    today = datetime.today()
    year = today.year
    month = today.month
    day = None
    

    # Handle navigation for previous and next months
    if "month" in request.GET and "year" in request.GET:
        month = int(request.GET["month"])
        year = int(request.GET["year"])
    elif request.method == "POST":
        # Preserve the selected month and year when a day is clicked
        month = int(request.POST.get("month", month))
        year = int(request.POST.get("year", year))
        day = int(request.POST.get("day"))  # Get the clicked day from the form

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

    #Also how to make it automatically create a calendar when seeded 

    # Handle form submission for selecting a day
    if request.method == "POST":
        bookings = Booking.objects.filter(student=request.user)
        week_days = get_week_days()
        events = []
        
        for booking in bookings:
            if booking.date == date(year,month,day):
                events.append(booking)
                print(booking)

    return render(
        request,
        'student_calendar.html',
        {
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
    )