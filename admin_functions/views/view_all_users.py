from django.views import View
from django.http import HttpResponseNotAllowed, HttpResponseForbidden, HttpResponse, HttpRequest
from django.shortcuts import redirect, render
from tutorials.models import User
from django.core.paginator import Paginator

class AllUsersView(View):

    def get(self, request: HttpRequest) -> HttpResponse:
        if not request.user.is_authenticated:
            return redirect('log_in')

        user_type = request.user.user_type
        if user_type != 'Admin':
            return render(request, 'permission_denied.html', status=403)

        users = User.objects.all()
        paginator = Paginator(users, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        user_count = User.objects.count()
        return render(request, 'view_users.html', {'page_obj': page_obj, 'count': user_count})


    def post(self, request: HttpRequest) -> HttpResponse:
        return HttpResponseNotAllowed("Requests to this URL must be made by the GET method!",
                                      content=b'Method Not Allowed', status=405)