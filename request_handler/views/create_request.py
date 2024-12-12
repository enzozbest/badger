from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views import View
from django.db.models import Max

from request_handler.forms import RequestForm
from request_handler.models.request_model import Request


class CreateRequestView(LoginRequiredMixin, View):
    """ Class to represent the creation of a request

    This class is used as a view for the website. This class defines the get() method to display a blank RequestForm instance,
    and the post() method to handle a filled in RequestForm instance.
    Both methods ensure that the user is authenticated and that its user type is Student or Admin.
    """

    def get(self, http_request: HttpRequest) -> HttpResponse:
        form = RequestForm()
        return render(http_request, 'create_request.html', {'form': form})

    def post(self, http_request: HttpRequest) -> HttpResponse:
        form = RequestForm(http_request.POST)
        if form.is_valid():

            #Get last group id to use for all of the new requests if recurring
            id = self.get_last_group_id()
            preform = form.save(commit=False)

            if form.cleaned_data['is_recurring']:
                term = form.cleaned_data['term']
                response = self.create_request(form, http_request, term, id)
                print(response)
                if response != "Late" and response != "Success":
                    form.add_error(error=f'There was an error submitting this form! {response}', field='term')
                print(term)
                if term == "September":
                    term = "January"
                    response = self.create_request(form, http_request, term, id)
                    if response != "Late" and response != "Success":
                        form.add_error(error=f'There was an error submitting this form! {response}', field='term')
                    print(term)
                print(response)
                if term == "January":
                    term = "May"
                    response = self.create_request(form, http_request, term, id)
                    if response != "Late" and response != "Success":
                        form.add_error(error=f'There was an error submitting this form! {response}', field='term')
                    print(term)
                print(response)
                if response == "Late":
                    return redirect('processing_late_request')
                elif response == "Success":
                    return redirect('request_success')
            else:
                term = form.cleaned_data['term']
                response = self.create_request(form, http_request, term, id)
                
                if response == "Late":
                    return redirect('processing_late_request')
                elif response == "Success":
                    return redirect('request_success')
                else:
                    form.add_error(error=f'There was an error submitting this form! {response}', field='term')

        return render(http_request, 'create_request.html', {'form': form})

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.is_tutor:
            return render(request, 'permission_denied.html', status=403)
        return super().dispatch(request, *args, **kwargs)

    def get_last_group_id(self):
        last_identifer = Request.objects.aggregate(Max('group_request_id'))['group_request_id__max']
        if last_identifer == None:
            return 1
        else:
            return (last_identifer + 1)

    def create_request(self, form, http_request, term, id):
        try:
            request_instance = Request(
                student=http_request.user,
                group_request_id=id,
                term=term,
                knowledge_area = form.cleaned_data['knowledge_area']
                
            )
            request_instance.save()

            # Manually add selected venues to Request instance.
            for mode in form.cleaned_data['venue_preference']:
                request_instance.venue_preference.add(mode)

            if form.is_late_request():
                request_instance.late = True
                request_instance.save()
                return "Late"
            else:
                request_instance.save()
                return "Success"

        except Exception as e:
            print(e)
            return e
            