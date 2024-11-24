from django.views import View
from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render, redirect, get_object_or_404
from user_system.models import User
from request_handler.models import Request

""" These classes allow admins to make selected users also admins and confirms their choice

Both classes take the primary key of the selected user as a parameter, allowing the user's record to be 
updated in the model.
Both classes require the Admin user type and redirect users to the login page if unauthenticated.
"""
class MakeUserAdmin(View):
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        return HttpResponseNotAllowed("Requests to this URL must be made by the GET method!",
                                      content=b'Method Not Allowed', status=405)
    
    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        if not request.user.is_authenticated:
            return redirect('log_in')
        
        user_type = request.user.user_type
        if user_type != 'Admin':
            return render(request, 'permission_denied.html', status=401)
        
        userToChange = User.objects.get(pk=pk)
        first_name = userToChange.first_name
        last_name = userToChange.last_name
        pk = userToChange.pk
        return render(request, 'make_user_admin.html', context={"first_name":first_name, "last_name":last_name, "pk":pk})
    
class ConfirmMakeUserAdmin(View):
    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        return HttpResponseNotAllowed("Requests to this URL must be made by the GET method!",
                                      content=b'Method Not Allowed', status=405)
    
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        requested_user_pk = pk
        if not request.user.is_authenticated:
            return redirect('log_in')
        
        user_type = request.user.user_type
        if user_type != 'Admin':
            return render(request, 'permission_denied.html', status=401)
        
        user_to_change = get_object_or_404(User, pk=requested_user_pk)
        user_to_change.user_type = "Admin"
        user_to_change.save()

        return render(request, 'confirm_make_user_admin.html', context={"user":user_to_change} )