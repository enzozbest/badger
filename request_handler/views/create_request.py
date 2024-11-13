from django.http import HttpRequest, HttpResponse
from django.views import View
from django.shortcuts import redirect, render
from request_handler.forms import RequestForm

""" Class to represent the creation of a request

This class is used as a view for the website. This class defines the get() method to display a blank RequestForm instance,
and the post() method to handle a filled in RequestForm instance.
Both methods ensure that the user is authenticated and that its user type is Student or Admin.
"""
class CreateRequestView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        if not request.user.is_authenticated:
            return redirect('log_in')

        if request.user.user_type == 'Tutor':
            return redirect('permission_denied')

        form = RequestForm()
        return render(request, 'create_request.html', {'form': form})

    def post(self, request: HttpRequest) -> HttpResponse:
        if not request.user.is_authenticated:
            return redirect('log_in')

        if not request.user.user_type == 'Student' or request.user.user_type=='Admin':
            return redirect('permission_denied')

        form = RequestForm(request.POST)

        if form.is_valid():
            try:
                request_instance = form.save(commit=False)
                request_instance.student = request.user
                request_instance.save()

                # Manually add selected days to Request instance.
                for day in form.cleaned_data['availability']:
                    request_instance.availability.add(day)

                # Manually add selected venues to Request instance.
                for mode in form.cleaned_data['venue_preference']:
                    request_instance.venue_preference.add(mode)
                
                request_instance.term = form.cleaned_data['term']
                return redirect('request_success')

            except Exception as e:
                form.add_error(error=f'There was an error submitting this form! {e}', field='term')
        else:
            return render(request, 'create_request.html', {'form': form})
