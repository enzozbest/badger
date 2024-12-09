"""
URL configuration for code_tutors project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.urls.conf import include

from admin_functions.views.view_cancellation_requests import ViewCancellationRequests
from calendar_scheduler.views.calendar import StudentCalendarView, TutorCalendarView
from calendar_scheduler.views.cancel_lessons import AdminCancelLessonsView, CancelLessonsView
from request_handler.views.accept_request import AcceptRequestView
from request_handler.views.reject_request import reject_request

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('user_system.urls')),
    path('requests/', include('request_handler.urls')),
    path('admins/', include('admin_functions.urls')),
    path('invoices/', include('invoicer.urls')),
    path('accept_request/<int:request_id>/', AcceptRequestView.as_view(), name="accept_request"),
    path('tutor/calendar/', TutorCalendarView.as_view(), name='tutor_calendar'),
    path('student/calendar/', StudentCalendarView.as_view(), name='student_calendar'),
    path('admin-tutor/calendar/<int:pk>/', TutorCalendarView.as_view(), name='admin_tutor_calendar'),
    path('admin-student/calendar/<int:pk>/', StudentCalendarView.as_view(), name='admin_student_calendar'),
    path('tutor/calendar/cancel/', CancelLessonsView.as_view(), name='tutor_cancel_lessons'),
    path('student/calendar/cancel/', CancelLessonsView.as_view(), name='student_cancel_lessons'),
    path('admins/calendar/cancel/', AdminCancelLessonsView.as_view(), name='admin_calendar_cancel_lessons'),
    path('admins/cancel/', CancelLessonsView.as_view(), name='admin_cancel_lessons'),
    path('admins/cancellation_requests/', ViewCancellationRequests.as_view(), name='view_cancellation_requests'),
    path('reject_request/<int:request_id>/', reject_request, name='reject_request'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
