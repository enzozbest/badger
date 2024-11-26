from calendar import Calendar

from django.shortcuts import render
from request_handler.models import Booking
from datetime import date, timedelta
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

def get_first_weekday(year, month, weekday):
    """
    Get the first occurrence of a specific weekday in a given month.

    Weekday parameter is the day that we would like the first of
    
    Returns a date object for the first occurrence of the specified weekday
    """
    # Start with the first day of the month
    first_day = date(year, month, 1)
    # Calculate the difference to the target weekday
    days_to_weekday = (weekday - first_day.weekday() + 7) % 7
    # Add the difference to the first day
    first_weekday = first_day + timedelta(days=days_to_weekday)
    return first_weekday

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
    '''
    bookings = Booking.objects.filter(student=request.user)
    week_days = get_week_days()
    calendar_data = {day: [] for day in week_days}
    for booking in bookings:
        for day in week_days:
            if booking.day and booking.day.day == day.strftime('%A'):
                calendar_data[day].append(booking)
    return render(request, 'student_calendar.html', {'week_days': week_days, 'calendar_data': calendar_data})
    '''
    calendar_slug = "student"
    try:
        calendar = Calendar.objects.get(slug=calendar_slug)
    except Calendar.DoesNotExist:
        return render(request, "calendar/error.html", {"message": "Calendar not found."})

    # Get today's date for the default display
    today = datetime.today()
    year = today.year
    month = today.month
    day = None
    month_days = get_month_days(year,month)
    events = []

    # Handle form submission for selecting a day
    if request.method == "POST":
        day = int(request.POST.get('day'))  # Get the clicked day from the form
        bookings = Booking.objects.filter(student=request.user)
        week_days = get_week_days()
        events = []
        print(bookings)
        daysList = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        
        for booking in bookings:
            #IF WE KNOW THE TERM, THE DAY, AND THE FREQUENCY, THEN WE CAN ADD THE SESSIONS TO THE CALENDAR 
            #WITHOUT STORING EACH INDIVIDUAL LESSON
            match booking.term:
                case "September":
                    start = get_first_weekday(year,9,daysList[day])
                case "January" if month>8:
                    start = get_first_weekday(year+1,1,daysList[day])
                case "January" if month<6:
                    start = get_first_weekday(year,1,daysList[day])
                case "May" if month>8:
                    start = get_first_weekday(year+1,5,daysList[day])
                case "May" if month<6:
                    start = get_first_weekday(year,5,daysList[day])
            
            for day in week_days:
                if booking.day and booking.day.day == day.strftime('%A'):
                    events.append(booking)
    return render(request,'student_calendar.html',{"calendar":calendar,"year":year,"month":month,"month_days":month_days,"events": events,"day":day})