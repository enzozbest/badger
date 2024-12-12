from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render
from django.views.generic.list import ListView

from admin_functions.helpers.mixins import SortingMixin
from calendar_scheduler.models import Booking


class ViewCancellationRequests(LoginRequiredMixin, ListView, SortingMixin):
    """ Class-based view to display all lesson cancellations that a user has requested
    Cancellations are only requested when the lesson is less than two weeks away
    Only Admin users can access this page
    """
    model = Booking
    context_object_name = 'cancelled'
    template_name = 'view_cancellation_requests.html'
    paginate_by = 20
    valid_sort_fields = ['id', 'student__full_name', 'tutor__full_name']

    def get_queryset(self):
        """Method that queries a cancelled bookings"""
        queryset = super().get_queryset().filter(cancellation_requested=True)
        return queryset

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.user_type == 'Admin':
            return render(request, 'permission_denied.html', status=403)
        return super().dispatch(request, *args, **kwargs)


def post(self, request: HttpRequest) -> HttpResponse:
    return HttpResponseNotAllowed("This URL only accepts GET requests.", status=405, content=b'Not Allowed')
