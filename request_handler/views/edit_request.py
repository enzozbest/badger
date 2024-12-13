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

        form.fields['term'].required = False
        term = request_instance.term
        vp = request_instance.venue_preference
        if form.is_valid():
            request_instance = form.save(commit=False)
            group = Request.objects.filter(group_request_id=request_instance.group_request_id).exclude(
                id=request_instance.id)
            if not request_instance.is_recurring:
                request_instance.save()
                form.save_m2m()
                group.all().delete()
                return redirect('view_requests')

            request_instance.term = term
            request_instance.save()
            form.save_m2m()
            request_instance.refresh_from_db()
            if not group.exists():
                fields = {'duration': request_instance.duration,
                          'frequency': request_instance.frequency,
                          'venue_preference': vp,
                          'knowledge_area': request_instance.knowledge_area, 'student': request_instance.student,
                          'group_request_id': request_instance.group_request_id,
                          'is_recurring': request_instance.is_recurring, }
                try:
                    create_recurring_requests(request_instance.term, fields)
                except ValueError:
                    form.add_error('term', "You cannot make this request recurring!")
                    request_instance.is_recurring = False
                    request_instance.save()
                    return render(request, 'edit_request.html',
                                  {'form': form, 'request_instance': request_instance})
            else:
                for group_request in group:
                    term = group_request.term
                    group_form = RequestForm(request.POST, {'term': term}, instance=group_request)
                    group_form.fields['term'].required = False
                    group_request = group_form.save(commit=False)
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


def create_recurring_requests(term: str, fields):
    match term:
        case 'September':
            fields['term'] = 'January'
            create_request(fields)
            create_recurring_requests('January', fields)
        case 'January':
            fields['term'] = 'May'
            create_request(fields)
        case None:
            fields['term'] = 'September'
            create_request(fields)
            create_recurring_requests('September', fields)
        case _:
            raise ValueError('Invalid term for recurring requests')


def create_request(data):
    obj = Request.objects.create(student=data['student'],
                                 knowledge_area=data['knowledge_area'],
                                 term=data['term'],
                                 frequency=data['frequency'],
                                 duration=data['duration'],
                                 group_request_id=data['group_request_id'],
                                 is_recurring=data['is_recurring']
                                 )
    obj.save()
    if data['venue_preference']:
        obj.venue_preference.set(data['venue_preference'].all())
    obj.save()
