from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from calendar_scheduler.models import Booking
from datetime import date


def cancel_day(id,day):
    lesson = Booking.objects.get(lesson_identifier=id, date=day)
    lesson.delete()

def cancel_term(id,month):
    months = []
    match month:
        case "9"|"10"|"11"|"12":
            print("winter")
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
    lesson = Booking.objects.filter(lesson_identifier=id)
    for i in lesson:
        i.delete()

class CancelLessonsView(LoginRequiredMixin,View):
    def get(self, request: HttpRequest) -> HttpResponse:
        if not(request.user.is_tutor or request.user.is_student):
            return render(request, 'permission_denied.html', status=401)
        day = request.GET.get("day")
        month = request.GET.get("month")
        year = request.GET.get("year")
        recurring = request.GET.get("recurring")
        lesson = request.GET.get('lesson')
        context = {"day":day, "month":month, "year":year, "recurring":recurring, "lesson":lesson}
        if request.user.is_tutor:
            return render(request,'tutor_cancel_lessons.html',context)
        else:
            return render(request,'student_cancel_lessons.html',context)
    
    def post(self, request: HttpRequest) -> HttpResponse:
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

        if request.user.is_student:
            return redirect('student_calendar')
        else:
            return redirect('tutor_calendar')