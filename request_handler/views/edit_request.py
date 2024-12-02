from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from request_handler.forms import RequestForm
from request_handler.models import Request


class EditRequestView(LoginRequiredMixin, View):
    """ Class-based view to represent editing a tutoring request's details."""

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        form, request_instance = self.get_form_and_instance(pk)
        return render(request, 'edit_request.html', {'form': form, 'request_instance': request_instance})

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        form, request_instance = self.get_form_and_instance(pk)
        form = RequestForm(request.POST, instance=request_instance)

        if not request.POST.getlist('venue_preference'):
            form.add_error('venue_preference', "No venue preference set!")

        if form.is_valid():
            request_instance = form.save(commit=False)
            request_instance.save()
            form.save_m2m()
            return redirect('view_requests')
        return render(request, 'edit_request.html', {'form': form, 'request_instance': request_instance})

    def get_form_and_instance(self, pk: int) -> tuple:
        request_instance = get_object_or_404(Request, pk=pk)
        form = RequestForm(instance=request_instance)
        return form, request_instance

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.is_tutor:
            return render(request, 'permission_denied.html', status=403)
        return super().dispatch(request, *args, **kwargs)
