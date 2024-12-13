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
            form.save(commit=False)
            terms = self.get_terms_to_process(form.cleaned_data['term'], form.cleaned_data['is_recurring'])
            has_late = False
            for term in terms:
                response = self.create_request(form, http_request, term, id)

                if response not in ("Late", "Success"):
                    form.add_error(field='term', error=f'There was an error submitting this form! {response}')
                    return render(http_request, 'create_request.html', {'form': form})
                if response == "Late":
                    has_late = True
            #Redirect at the end if it's late
            if has_late:
                return redirect('processing_late_request')

            return redirect('request_success')

        return render(http_request, 'create_request.html', {'form': form})

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.is_tutor:
            return render(request, 'permission_denied.html', status=403)
        return super().dispatch(request, *args, **kwargs)

    def get_last_group_id(self):
        """ Returns the last group id + 1 used in the Request model
        Group ids are used to group together recurring requests
        If this is the first request, then we return 1
        """
        last_identifer = Request.objects.aggregate(Max('group_request_id'))['group_request_id__max']
        if last_identifer == None:
            return 1
        else:
            return (last_identifer + 1)

    def get_terms_to_process(self, initial_term, is_recurring):
        """Determine the terms to process based on recurrence."""
        terms = [initial_term]

        if is_recurring:
            term_sequence = {"September": "January", "January": "May"}
            while terms[-1] in term_sequence:
                terms.append(term_sequence[terms[-1]])

        return terms

    def create_request(self, form, http_request, term, id):
        """ Creates the request object for database storage"""
        try:
            request_instance = Request(
                student=http_request.user,
                group_request_id=id,
                term=term,
                knowledge_area = form.cleaned_data['knowledge_area'],
                frequency=form.cleaned_data['frequency'],
                is_recurring=form.cleaned_data['is_recurring']
                
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
            return e
            