from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import date,datetime,timedelta, time
from request_handler.models import Request
from calendar_scheduler.models import Booking
from django.db.models import Max


def get_first_weekday(year, month, target_day):
    """
    Get the first occurrence of a specific weekday in a given month.

    Weekday parameter is the day that we would like the first of as an Int

    Returns a date object for the first occurrence of the specified weekday
    """
    # Start with the first day of the month
    first_day = date(year, month, 1)
    first_day_weekday = first_day.weekday() 
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day = weekdays.index(target_day.day)
    days_to_target = (day - first_day_weekday + 7) % 7
    target = first_day + timedelta(days=days_to_target)
    lesson_time = time(12,0)
    return datetime.combine(target,lesson_time)

class AcceptRequestView(LoginRequiredMixin, View):
    def post(self, request, request_id):
        lesson_request = get_object_or_404(Request, id=request_id, allocated=True, tutor=request.user)

        today = datetime.today()
        current_year = today.year
        current_month = today.month
        first_term = lesson_request.term
        match first_term:
            case "September":
                booking_date = get_first_weekday(current_year,9,lesson_request.day)
            case "January" if current_month>8:
                booking_date = get_first_weekday(current_year+1,1,lesson_request.day)
            case "January" if current_month<6:
                booking_date = get_first_weekday(current_year,1,lesson_request.day)
            case "May" if current_month>8:
                booking_date = get_first_weekday(current_year+1,5,lesson_request.day)
            case "May" if current_month<6:
                booking_date = get_first_weekday(current_year,5,lesson_request.day)
            case _:
                return redirect('view_requests')

        sessions = 0
        match lesson_request.frequency:
            case "Weekly":
                sessions = 15
            case "Biweekly":
                sessions = 30
            case "Fortnightly":
                sessions = 7
            case _:
                return redirect('view_requests')

        # Retrieves the lesson_identifier of the last group of bookings
        last_identifier = Booking.objects.aggregate(Max('lesson_identifier'))['lesson_identifier__max']
        if last_identifier == None:
            new_identifier = 1
        else:
            new_identifier = last_identifier + 1

        # Now add each of the sessions, starting with the booking_date
        for i in range(0,sessions):
            try:
                # Create a new Booking object based on the allocated request
                Booking.objects.create(
                    lesson_identifier = new_identifier,
                    tutor=request.user,
                    student=lesson_request.student,
                    knowledge_area=lesson_request.knowledge_area,
                    venue=lesson_request.venue,
                    day=lesson_request.day,
                    term=lesson_request.term,
                    frequency=lesson_request.frequency,
                    duration=lesson_request.duration,
                    is_recurring=lesson_request.is_recurring,
                    date=booking_date.date(),
                    start= booking_date,
                    end=booking_date,
                    title = f"Tutor session between {lesson_request.student.first_name} {lesson_request.student.last_name} and {lesson_request.tutor_name}"
                )
                match lesson_request.frequency:
                    case "Weekly":
                        booking_date += timedelta(days=7)
                    case "Biweekly":
                        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                        day1 = weekdays.index(str(lesson_request.day))
                        day2 = weekdays.index(str(lesson_request.day2))
                        if booking_date.weekday() == day1:
                            #Find the difference from day1 to day2
                            dayDiff = (day2-day1 + 7) % 7
                            booking_date += timedelta(days=dayDiff)
                        else:
                            #Find the difference from day2 to day1
                            dayDiff = (day1 - booking_date.weekday() + 7) % 7
                            booking_date += timedelta(days=dayDiff)
                    case "Fortnightly":
                        booking_date += timedelta(days=14)

            except Exception as e:
                return redirect('view_requests')

        lesson_request.delete()
        return redirect('view_requests')

