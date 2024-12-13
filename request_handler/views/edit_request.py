from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from request_handler.forms import RequestForm
from request_handler.models.request_model import Request


class EditRequestView(LoginRequiredMixin, View):
    """ Class-based view to represent editing a tutoring request's details."""

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        form, request_instance = self.get_form_and_instance(pk)
        if request_instance.is_recurring:
            form.fields['term'].disabled = True
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

            group = Request.objects.filter(group_request_id=request_instance.group_request_id).exclude(
                id=request_instance.id)
            request_instance.refresh_from_db()
            if not request_instance.is_recurring:
                group.all().delete()
            else:
                if not group.exists():
                    pass  # Create recurring requests here (how?)
                for group_request in group:
                    term = group_request.term
                    group_form = RequestForm(request.POST, instance=group_request)
                    try:
                        group_request = group_form.save(commit=False)
                    except Exception as e:
                        print(e)
                        # return redirect('view_requests')

                    group_request.save()
                    group_form.save_m2m()
                    group_request.term = term
                    group_request.save()
            return redirect('view_requests')
        return render(request, 'edit_request.html', {'form': form, 'request_instance': request_instance})

    def get_form_and_instance(self, pk: int) -> tuple:
        request_instance = get_object_or_404(Request, pk=pk)
        form = RequestForm(instance=request_instance)
        return form, request_instance

    def dispatch(self, wsgi_request, *args, **kwargs):
        if not wsgi_request.user.is_authenticated:
            return self.handle_no_permission()

        pk = kwargs.get('pk') or wsgi_request.POST.get('pk') or wsgi_request.GET.get('pk')
        try:
            _, instance = self.get_form_and_instance(pk)
            if wsgi_request.user.is_tutor or (
                    wsgi_request.user.is_student and wsgi_request.user.id != instance.student.id):
                return render(wsgi_request, 'permission_denied.html', status=403)
        except Http404:
            pass
        return super().dispatch(wsgi_request, *args, **kwargs)
