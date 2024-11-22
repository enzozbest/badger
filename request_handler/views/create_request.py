from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.views import View
from django.shortcuts import redirect, render
from request_handler.forms import RequestForm

""" Class to represent the creation of a request

This class is used as a view for the website. This class defines the get() method to display a blank RequestForm instance,
and the post() method to handle a filled in RequestForm instance.
Both methods ensure that the user is authenticated and that its user type is Student or Admin.
"""
class CreateRequestView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest) -> HttpResponse:
        if request.user.is_tutor:
            return render(request, 'permission_denied.html', status=401)

        form = RequestForm()
        return render(request, 'create_request.html', {'form': form})

    def post(self, request: HttpRequest) -> HttpResponse:
        if not request.user.is_authenticated:
            return redirect('log_in')

        if request.user.is_tutor:
            return render(request, 'permission_denied.html', status=401)

        form = RequestForm(request.POST)

        if form.is_valid():
            try:
                request_instance = form.save(commit=False)
                request_instance.student = request.user
                request_instance.save()

                # Manually add selected venues to Request instance.
                for mode in form.cleaned_data['venue_preference']:
                    request_instance.venue_preference.add(mode)
                
                request_instance.term = form.cleaned_data['term']
                
                #Redirect the user to a page that is static for 5 seconds, allowing them to see the warning
                if form.is_late_request():
                    request_instance.late = True
                    request_instance.save()
                    return redirect('processing_late_request')
                else:
                    return redirect('request_success')

            except Exception as e:
                form.add_error(error=f'There was an error submitting this form! {e}', field='term')
        return render(request, 'create_request.html', {'form': form})
