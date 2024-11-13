from django.views import View
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from request_handler.models import Request

class ViewRequest(View):
    """Provides a list of all requests made by the signed in student

    Redirects user to login page if they aren't authenticated
   """
    def get(self, request: HttpRequest) -> HttpResponse:
        if not request.user.is_authenticated:
            return redirect('log_in')

        user_type = request.user.user_type
        user_request = None
        context = {'requests': [], 'user_type': user_type}
        match user_type:
            case 'Student':
                user_request = list(Request.objects.filter(student=request.user))
            case 'Tutor':
                user_request = list(Request.objects.filter(tutor=request.user))
            case 'Admin':
                user_request = Request.objects.all()

        if user_request:
            context = {'requests': user_request, 'user_type': user_type}

        return render(request, 'view_users.html', context)

    def post(self, request: HttpRequest) -> HttpResponse:
        return HttpResponseBadRequest('This URL does not accept POST requests')
