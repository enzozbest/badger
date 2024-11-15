from django.views import View
from django.http import HttpResponseNotAllowed, HttpResponse, HttpRequest
from django.shortcuts import redirect, render
from user_system.models import User
from django.core.paginator import Paginator
from admin_functions.helpers.filters import UserFilter

class AllUsersView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        if not request.user.is_authenticated:
            return redirect('log_in')

        user_type = request.user.user_type
        if user_type != 'Admin':
            return render(request, 'permission_denied.html', status=403)

        users = User.objects.all()
        filter_obj = UserFilter(request.GET, queryset=users)
        filtered_users = filter_obj.qs
        paginator = Paginator(filtered_users, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        user_count = User.objects.count()
        return render(request, 'view_users.html', {'page_obj': page_obj, 'count': user_count, 'filter':filter_obj})


    def post(self, request: HttpRequest) -> HttpResponse:
        return HttpResponseNotAllowed("Requests to this URL must be made by the GET method!",
                                      content=b'Method Not Allowed', status=405)