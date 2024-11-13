from django.views import View
from django.http import HttpResponseNotAllowed, HttpResponseForbidden, HttpResponse, HttpRequest
from django.shortcuts import redirect, render
from tutorials.models import User


class AllUsersView(View):

    def get(self, request: HttpRequest) -> HttpResponse:
        if not request.user.is_authenticated:
            return redirect('log_in')

        user_type = request.user.user_type
        if user_type != 'Admin':
            return render(request, 'request_handler/templates/permission_denied', status=403)

        users = User.objects.all()
        user_count = User.objects.count()
        return render(request, 'view_users.html', {'users' : users, 'count': user_count})


    def post(self, request: HttpRequest) -> HttpResponse:
        return HttpResponseNotAllowed("Requests to this URL must be made by the GET method!", status=405)