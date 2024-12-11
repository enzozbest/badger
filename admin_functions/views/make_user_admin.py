from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, render
from django.views import View

from user_system.models.user_model import User

""" These classes allow admins to make selected users also admins and confirms their choice

  Both classes take the primary key of the selected user as a parameter, allowing the user's record to be
  updated in the model.
  Both classes require the Admin user type and redirect users to the login page if unauthenticated.
  """


class MakeUserAdmin(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        return HttpResponseNotAllowed("[GET]",
                                      content=b'Method Not Allowed', status=405)

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        userToChange = User.objects.get(pk=pk)
        first_name = userToChange.first_name
        last_name = userToChange.last_name
        pk = userToChange.pk
        return render(request, 'make_user_admin.html',
                      context={"first_name": first_name, "last_name": last_name, "pk": pk})

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_admin:
            return render(request, 'permission_denied.html', status=403)
        return super().dispatch(request, *args, **kwargs)


class ConfirmMakeUserAdmin(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        return HttpResponseNotAllowed("[POST, PUT, PATCH]",
                                      content=b'Method Not Allowed', status=405)

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        requested_user_pk = pk
        user_to_change = get_object_or_404(User, pk=requested_user_pk)
        user_to_change.user_type = "Admin"
        user_to_change.save()

        return render(request, 'confirm_make_user_admin.html', context={"user": user_to_change})

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_admin:
            return render(request, 'permission_denied.html', status=403)
        return super().dispatch(request, *args, **kwargs)
