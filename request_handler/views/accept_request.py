from datetime import date, datetime, time, timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Max
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from calendar_scheduler.models import Booking
from request_handler.models.request_model import Request


def get_first_weekday(year, month, target_day):
    """Get the first occurrence of a specific weekday in a given month.

    Returns a date object for the first occurrence of the specified weekday.
    """
    first_day = date(year, month, 1)
    first_day_weekday = first_day.weekday()
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day = weekdays.index(target_day.day)
    days_to_target = (day - first_day_weekday + 7) % 7
    target = first_day + timedelta(days=days_to_target)
    lesson_time = time(12, 0)
    return datetime.combine(target, lesson_time)


class AcceptRequestView(LoginRequiredMixin, View):
    """Class-based view for the tutor to accept a request once it has been allocated to them.

    The AcceptRequestView allows a Tutor user to accept a request from a student whose current allocation status is
    set to "allocated". This view is responsible for turning the request into a booking and storing the lessons
    which will be shown in the calendar.
    """

    def post(self, request, request_id):
        lesson_request = get_object_or_404(Request, id=request_id, allocated=True, tutor=request.user)
        sessions = self.calculate_lesson_frequency(lesson_request)
        new_identifier = self.get_last_identifier()
        grouped_lessons = self.get_grouped_lessons(lesson_request.group_request_id)

        for lesson in grouped_lessons:
            booking_date = self.get_booking_start_date(lesson_request)
            result = self.create_bookings(sessions, new_identifier, request, lesson, booking_date)
            if result != "":
                print(result)
                return redirect('view_requests')
            else:
                lesson.delete()
        return redirect('view_requests')

    def get_last_identifier(self):
        """Retrieves the lesson_identifier of the last group of bookings."""

        last_identifier = Booking.objects.aggregate(Max('lesson_identifier'))['lesson_identifier__max']
        if last_identifier == None:
            return 1
        else:
            return (last_identifier + 1)

    def get_booking_start_date(self, lesson_request):
        """Gets the start date of the booking."""

        today = datetime.today()
        current_year = today.year
        current_month = today.month
        first_term = lesson_request.term
        return self.match_term(lesson_request, first_term, current_year, current_month)

    def match_term(self, lesson_request, first_term, current_year, current_month):
        """Matches the term of the request to a term that exists in the year."""
        match first_term:
            case "September":
                booking_date = get_first_weekday(current_year, 9, lesson_request.day)
            case "January" if current_month > 8:
                booking_date = get_first_weekday(current_year + 1, 1, lesson_request.day)
            case "January" if current_month < 6:
                booking_date = get_first_weekday(current_year, 1, lesson_request.day)
            case "May" if current_month > 8:
                booking_date = get_first_weekday(current_year + 1, 5, lesson_request.day)
            case "May" if current_month < 6:
                booking_date = get_first_weekday(current_year, 5, lesson_request.day)
            case _:
                booking_date = None
        return booking_date

    def calculate_lesson_frequency(self, lesson_request):
        """Calculates how many lessons are required depending on the frequency of the request."""

        match lesson_request.frequency:
            case "Weekly":
                return 15
            case "Biweekly":
                return 30
            case "Fortnightly":
                return 7
            case _:
                return 0

    def match_lesson_frequency(self, lesson_request, booking_date):
        """Matches the frequency of the request to put into the calendar."""
        match lesson_request.frequency:
            case "Weekly":
                booking_date += timedelta(days=7)
            case "Biweekly":
                weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                day1 = weekdays.index(str(lesson_request.day))
                day2 = weekdays.index(str(lesson_request.day2))
                if booking_date.weekday() == day1:
                    # Find the difference from day1 to day2
                    dayDiff = (day2 - day1 + 7) % 7
                    booking_date += timedelta(days=dayDiff)
                else:
                    # Find the difference from day2 to day1
                    dayDiff = (day1 - booking_date.weekday() + 7) % 7
                    booking_date += timedelta(days=dayDiff)
            case "Fortnightly":
                booking_date += timedelta(days=14)
            case _:
                raise ValueError('This frequency is invalid')

        return booking_date

    def get_grouped_lessons(self,id):
        lessons = Request.objects.filter(group_request_id=id).all()
        return lessons

    def create_bookings(self, sessions, new_identifier, request, lesson_request, booking_date):
        # Now add each of the sessions, starting with the booking_date
        for i in range(0, sessions):
            try:
                # Create a new Booking object based on the allocated request
                Booking.objects.create(
                    lesson_identifier=new_identifier,
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
                    title=f"Tutor session between {lesson_request.student.first_name} {lesson_request.student.last_name} and {lesson_request.tutor_name}"
                )
                booking_date = self.match_lesson_frequency(lesson_request, booking_date)
            except Exception as e:
                return e
        return ""