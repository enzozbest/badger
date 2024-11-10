from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from request_handler.models import Request
from request_handler.forms import RequestForm

class EditRequestView(View):
    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        if request.user.user_type == 'Tutor':
            return redirect('permission_denied', {'user_type': 'Tutor'})

        form = self.get_form(pk)
        return render(request, 'edit_request.html', {'form': form})

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        if request.user.user_type == 'Tutor':
            return redirect('permission_denied', {'user_type': 'Tutor'})

        form = self.get_form(pk)
        if form.is_valid():
            request_instance = form.save(commit=False)
            request_instance.save()
            form.save_m2m()
            if not request_instance.venue_preference.exists():
                form.add_error('venue_preference', "No venue preference set!")
            else:
                return redirect('view_requests')
        else:
            return self.get(request, pk)
        return render(request, 'edit_request.html', {'form': form, 'request_instance': request_instance})

    def get_form(self, pk:int) -> RequestForm:
        request_instance = get_object_or_404(Request, pk=pk)
        form = RequestForm(instance=request_instance)
        return form