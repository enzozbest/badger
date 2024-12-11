from django.urls.conf import path

from calendar_scheduler.views.calendar import StudentCalendarView, TutorCalendarView
from calendar_scheduler.views.cancel_lessons import AdminCancelLessonsView, CancelLessonsView

urlpatterns = [
    path('tutor/', TutorCalendarView.as_view(), name='tutor_calendar'),
    path('student/', StudentCalendarView.as_view(), name='student_calendar'),
    path('admin-tutor/<int:pk>/', TutorCalendarView.as_view(), name='admin_tutor_calendar'),
    path('admin-student/<int:pk>/', StudentCalendarView.as_view(), name='admin_student_calendar'),
    path('tutor/cancel/', CancelLessonsView.as_view(), name='tutor_cancel_lessons'),
    path('student/cancel/', CancelLessonsView.as_view(), name='student_cancel_lessons'),
    path('admins/cancel/', AdminCancelLessonsView.as_view(), name='admin_calendar_cancel_lessons'),
    path('admins/lessons/cancel/', CancelLessonsView.as_view(), name='admin_cancel_lessons'),
]
