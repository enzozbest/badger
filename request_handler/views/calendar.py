from calendar import Calendar

from django.shortcuts import render
from request_handler.models import Booking
from datetime import date, timedelta

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

def student_calendar(request):
    if not request.user.is_student:
        return render(request, '403.html') # Make this file

    bookings = Booking.objects.filter(student=request.user)
    week_days = get_week_days()
    calendar_data = {day: [] for day in week_days}
    for booking in bookings:
        for day in week_days:
            if booking.day and booking.day.day == day.strftime('%A'):
                calendar_data[day].append(booking)
    return render(request, 'student_calendar.html', {'week_days': week_days, 'calendar_data': calendar_data})