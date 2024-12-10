from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from calendar_scheduler.models import Booking
from datetime import date, datetime, timedelta

def cancel_day(id, day):
    ''' Cancels an individual lesson, determined by the id and the lessons date '''
    try:
        lesson = Booking.objects.get(lesson_identifier=id, date=day)
        lesson.delete()
    except Booking.DoesNotExist:
        return HttpResponseNotFound(f"Booking with lesson_identifier={id} and date={day} doesn't seem to exist.")

def cancel_term(id,month):
    ''' Cancels all lessons for a term, where the term is determined by the month of requested cancelation '''
    months = []
    match month:
        case "9"|"10"|"11"|"12":
            months = [9,10,11,12]
        case "1"|"2"|"3"|"4":
            months = [1,2,3,4]
        case "5"|"6"|"7":
            months = [5,6,7]

    for current_month in months:
        lessons = Booking.objects.filter(lesson_identifier=id, date__month=current_month)
        for lesson in lessons:
            lesson.delete()

def cancel_recurring(id):
    ''' Cancels all lesson that are a part of a recurring booking, based on the id they share'''
    lesson = Booking.objects.filter(lesson_identifier=id)
    for i in lesson:
        i.delete()

def student_tutor_cancel(request,):
    '''This method is used to match the type of cancellation the user is requesting. '''
    day = request.POST.get("day")
    month = request.POST.get("month")
    year = request.POST.get("year")
    lesson_id = request.POST.get("lesson")
    cancellation = request.POST.get("cancellation")

    #Delete lessons from the database, according to whether the user only wants to delete:
    #The lesson for that specific day
    #The lessons for that term
    #All lessons if it's a recurring request
    match cancellation:
        case "day":
            day = date(int(year),int(month),int(day))
            cancel_day(lesson_id,day)
        case "term":
            cancel_term(lesson_id,month)
        case "recurring":
            cancel_recurring(lesson_id)
        case "request":
            #Set the cancellation_requested field to true
            day = date(int(year),int(month),int(day))
            lesson = Booking.objects.get(lesson_identifier=lesson_id, date=day)
            lesson.cancellation_requested = True
            lesson.save()
    return

def check_close_cancellation(year, month, day, recurring, lesson):
    ''' This method checks whether the date the user has requested to cancel is too close (<2 weeks)
    Such dates require admin approval
    '''
    cancel_day = date(int(year),int(month),int(day))
    dayDatetime = datetime.combine(cancel_day, datetime.min.time())
    today = datetime.now()
    if (dayDatetime - today) >= timedelta(days=14):
        close_date = False
    else:
        close_date = True
    context = {"day":day, "month":month, "year":year, "recurring":recurring, "lesson":lesson, "close_date": close_date}

""" These classes allow users to cancel lessons from the calendar.

Both classes get the specific date of the lesson that the cancel button was clicked for and render
the appropriate templates depending on the user attempting to cancel (student, tutor or admin). 
The classes deal with day, term and recurring cancellations and for students and tutors in particular, 
there is an option to request a cancellation (admins do not need to request to cancel a lesson). 
"""
class CancelLessonsView(LoginRequiredMixin,View):
    def get(self, request: HttpRequest) -> HttpResponse:
        if not(request.user.is_tutor or request.user.is_student):
            return render(request, 'permission_denied.html', status=401)
        day = request.GET.get("day")
        month = request.GET.get("month")
        year = request.GET.get("year")
        recurring = request.GET.get("recurring")
        lesson = request.GET.get('lesson')

        context = check_close_cancellation(year,month,day, recurring, lesson)
        if request.user.is_tutor:
            return render(request,'tutor_cancel_lessons.html', context)
        elif request.user.is_student:
            return render(request,'student_cancel_lessons.html', context)

    def post(self, request: HttpRequest) -> HttpResponse:
        if request.user.is_student or request.user.is_tutor:
            student_tutor_cancel(request)
            if request.user.is_student:
                return redirect('student_calendar')
            else:
                return redirect('tutor_calendar')
        elif request.user.user_type == "Admin" and request.POST.get('cancellation')=="accept":
            lesson_id = request.POST.get("lesson")
            lesson = Booking.objects.get(id=lesson_id)
            lesson.delete()
            #Return to admin view cancellation requests
            return redirect('view_cancellation_requests')
        elif request.user.user_type == "Admin" and request.POST.get('cancellation')=="reject":
            #Just delete the cancellation request, i.e. change the cancellation_requested field to false
            lesson_id = request.POST.get("lesson")
            lesson = Booking.objects.get(id=lesson_id)
            lesson.cancellation_requested = False
            lesson.save()
            return redirect('view_cancellation_requests')

class AdminCancelLessonsView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest) -> HttpResponse:
        day = request.GET.get("day")
        month = request.GET.get("month")
        year = request.GET.get("year")
        recurring = request.GET.get("recurring")
        lesson_id = request.GET.get("lesson")

        # Confirm whether the cancellation window is open (e.g., >= 2 weeks before the lesson)
        context = check_close_cancellation(year, month, day, recurring, lesson_id)
        return render(request, 'admin_cancel_lessons.html', context)

    def post(self, request: HttpRequest) -> HttpResponse:
        lesson_id = request.POST.get("lesson")
        cancellation = request.POST.get("cancellation")
        day = request.POST.get("day")
        month = request.POST.get("month")
        year = request.POST.get("year")

        try:
            match cancellation:
                case "day":
                    cancel_one_day = date(int(year),int(month),int(day))
                    self.cancel_single_lesson_admin(lesson_id, cancel_one_day)
                case "term":
                    cancel_term(lesson_id,month)
                case "recurring":
                    cancel_recurring(lesson_id)
                case _:
                    return HttpResponse("Invalid cancellation type.", status=400)
        except Exception as e:
            return HttpResponse(f"Error processing cancellation: {e}", status=500)

        return redirect('view_all_users') # change this maybe

    # repetitive so will need refactoring
    def cancel_single_lesson_admin(self, lesson_id, cancel_one_day):
        booking = Booking.objects.filter(lesson_identifier=lesson_id, date=cancel_one_day)
        if not booking:
            raise ValueError(f"No booking found for lesson_id: {lesson_id} on {cancel_one_day}")
        booking.delete()
