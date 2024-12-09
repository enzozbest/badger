from django.views import View
from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from calendar_scheduler.models import Booking

from admin_functions.helpers.cancellation_request_filter import CancellationRequestFilter
from admin_functions.helpers.mixins import SortingMixin

class ViewCancellationRequests(SortingMixin, View):
    
    models=Booking
    paginate_by = 5
    filterset_class = CancellationRequestFilter
    valid_sort_fields = {
        'id': 'ID',
        'student__first_name': 'Student',
        'tutor__first_name': 'Tutor',
        'date': 'Date'}
    
    def get(self, request: HttpRequest) -> HttpResponse:
        if not request.user.is_authenticated:
            return redirect('log_in')
        if request.user.user_type != 'Admin':
            return render(request, 'permission_denied.html', status=403)
        
        requested_lessons = Booking.objects.filter(cancellation_requested=True)
        if hasattr(self, 'filterset_class'):
            self.filterset = self.filterset_class(self.request.GET, queryset=requested_lessons)
            if self.filterset.is_valid():
                requested_lessons = self.filterset.qs
        requested_lessons = self.get_sorting_queryset(requested_lessons)

        paginator = Paginator(requested_lessons, self.paginate_by)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        current_sort = request.GET.get('sort', 'id')
        return render(request, 'view_cancellation_requests.html', 
                      context={'filter': self.filterset,
                               'lessons':page_obj,
                               'current_sort': current_sort,
                               'page_obj': page_obj})
    
    def post(self, request: HttpRequest) -> HttpResponse:
        return HttpResponseNotAllowed("This URL only accepts GET requests.", status=405, content=b'Not Allowed')