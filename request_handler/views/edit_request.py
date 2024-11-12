from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from request_handler.models import Request
from request_handler.forms import RequestForm

class EditRequestView(View):
    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        if request.user.user_type == 'Tutor':
            return redirect('permission_denied')

        form, request_instance = self.get_form_and_instance(pk)
        return render(request, 'edit_request.html', {'form': form, 'request_instance': request_instance})

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        if request.user.user_type == 'Tutor':
            return render(request, 'permission_denied.html', status=403)
        
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