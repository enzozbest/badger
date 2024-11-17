from django.views import View
from django.http import HttpResponseNotAllowed, HttpResponse, HttpRequest
from django.shortcuts import redirect, render
from request_handler.models import Request
from django.core.paginator import Paginator
from admin_functions.helpers.filters import AllocationFilter
from django.db.models import Q

class AllRequestsView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        if not request.user.is_authenticated:
            return redirect('log_in')

        user_type = request.user.user_type

        requests = Request.objects.all()
        filter_obj = AllocationFilter(request.GET, queryset=requests)
        filtered_requests = filter_obj.qs.order_by('pk')

        if request.user.user_type == 'Student':
            filtered_requests = filtered_requests.filter(student=request.user)
        if request.user.user_type == 'Tutor':
            filtered_requests = filtered_requests.filter(tutor=request.user)

        paginator = Paginator(filtered_requests, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        request_count = filtered_requests.count()
        context = {
            'requests': requests,
            'user_type': user_type,
            'page_obj': page_obj,
            'count': request_count,
            'filter': filter_obj,
        }
        return render(request, 'view_requests.html', context)

    def post(self, request: HttpRequest) -> HttpResponse:
        return HttpResponseNotAllowed("Requests to this URL must be made by the GET method!",
                                      content=b'Method Not Allowed', status=405)
