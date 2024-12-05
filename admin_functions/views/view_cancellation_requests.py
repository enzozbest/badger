from django.views import View
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from calendar_scheduler.models import Booking

class ViewCancellationRequests(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        if not request.user.is_authenticated:
            return redirect('log_in')
        
        user_type = request.user.user_type
        if user_type != 'Admin':
            return render(request, 'permission_denied.html', status=401)
        
        requested_lessons = Booking.objects.filter(cancellation_requested=True)
        print(requested_lessons)
        return render(request, 'view_cancellation_requests.html', context={'lessons':requested_lessons})
        