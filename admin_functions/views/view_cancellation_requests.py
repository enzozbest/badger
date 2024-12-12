from django.views import View
from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render, redirect
from calendar_scheduler.models import Booking


class ViewCancellationRequests(View):
    """ Class-based view to display all lesson cancellations that a user has requested
    Cancellations are only requested when the lesson is less than two weeks away
    Only Admin users can access this page
    """
    def get(self, request: HttpRequest) -> HttpResponse:
        if not request.user.is_authenticated:
            return redirect('log_in')
        if request.user.user_type != 'Admin':
            return render(request, 'permission_denied.html', status=403)
        
        sort = request.GET.get('sort', '')
        
        requested_lessons = Booking.objects.filter(cancellation_requested=True)

        if sort:
            try:
                requested_lessons = requested_lessons.order_by(sort)
            except Exception as e:
                # Handle invalid sorting keys (optional logging)
                print(f"Invalid sort key: {sort}. Error: {e}")



        return render(request, 'view_cancellation_requests.html', context={'lessons':requested_lessons})
    
    def post(self, request: HttpRequest) -> HttpResponse:
        return HttpResponseNotAllowed("This URL only accepts GET requests.", status=405, content=b'Not Allowed')