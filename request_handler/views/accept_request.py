from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime,date,timedelta
from request_handler.models import Request, Booking

def get_first_weekday(year, month, day):
        """
        Get the first occurrence of a specific weekday in a given month.

        Weekday parameter is the day that we would like the first of as an Int
        
        Returns a date object for the first occurrence of the specified weekday
        """
        # Start with the first day of the month
        first_day = date(year, month, 1)
        # Calculate the difference to the target weekday
        daysList = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        days_to_weekday = (daysList.index(day.day) - first_day.day + 7) % 7
        # Add the difference to the first day
        first_weekday = first_day + timedelta(days=days_to_weekday + 1)
        return first_weekday

class AcceptRequestView(LoginRequiredMixin, View):
    def post(self, request, request_id):
        lesson_request = get_object_or_404(Request, id=request_id, allocated=True, tutor=request.user)
        #Bookings will be created as lessons, i.e. there will be a booking per session 
        #We need lesson_request.frequency
        #lesson_request.is_recurring

        today = datetime.today()
        current_year = today.year
        current_month = today.month
        first_term = lesson_request.term
        
        #Remember 15 week terms
        match first_term:
            case "September":
                #We want to find the first date in september where it matches the chosen day
                booking_date = get_first_weekday(current_year,9,lesson_request.day)
            case "January" if current_month>8:
                booking_date = get_first_weekday(current_year+1,1,lesson_request.day)
            case "January" if current_month<6:
                booking_date = get_first_weekday(current_year,1,lesson_request.day)
            case "May" if current_month>8:
                booking_date = get_first_weekday(current_year+1,5,lesson_request.day)
            case "May" if current_month<6:
                booking_date = get_first_weekday(current_year,5,lesson_request.day)

        #How does biweekly work, since we would need two days for the allocated request

        session = 0
        match lesson_request.frequency:
            case "Weekly":
                sessions = 15
            case "Biweekly":
                sessions = 30
            case "Fortnightly":
                sessions = 7

        #Now add each of the sessions, starting with the booking_date
        for i in range(0,sessions):
            try:
                # Create a new Booking object based on the allocated request
                Booking.objects.create(
                    tutor=request.user,
                    student=lesson_request.student,
                    knowledge_area=lesson_request.knowledge_area,
                    venue=lesson_request.venue,
                    day=lesson_request.day,
                    term=lesson_request.term,
                    frequency=lesson_request.frequency,
                    duration=lesson_request.duration,
                    is_recurring=lesson_request.is_recurring,
                    date=booking_date,
                )
                match lesson_request.frequency:
                    case "Weekly":
                        booking_date += timedelta(days=7)
                    case "Biweekly":
                        booking_date += timedelta(days=3)
                        #Is this fine, since we didn't discuss 2 day availability
                    case "Fortnightly":
                        booking_date += timedelta(days=14)

            except Exception as e:
                print(f"Error creating booking: {e}")
            
        lesson_request.delete()
        return redirect('view_requests')

    