from django.views import View
from django.http import HttpResponseNotAllowed, HttpResponse, HttpRequest
from django.shortcuts import redirect, render
from request_handler.models import Request
from django.core.paginator import Paginator
from admin_functions.helpers.filters import AllocationFilter

class AllRequestsView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        if not request.user.is_authenticated:
            return redirect('log_in')

        user_type = request.user.user_type
        if user_type != 'Admin':
            return render(request, 'permission_denied.html', status=403)

        requests = Request.objects.all()
        filter_obj = AllocationFilter(request.GET, queryset=requests)
        filtered_requests = filter_obj.qs

        paginator = Paginator(filtered_requests, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        request_count = Request.objects.count()
        context = {
            'requests': requests,
            'page_obj': page_obj,
            'count': request_count,
            'filter': filter_obj,
        }

        return render(request, 'view_all_requests.html', context)


    def post(self, request: HttpRequest) -> HttpResponse:
        return HttpResponseNotAllowed("Requests to this URL must be made by the GET method!",
                                      content=b'Method Not Allowed', status=405)
