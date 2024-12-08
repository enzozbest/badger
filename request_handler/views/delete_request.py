from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from request_handler.models import Request


class DeleteRequestView(LoginRequiredMixin, View):
    """ Class-based view for deletion of a request

    This class is used as a view for the website. This class defines the get() method to return an error as get requests
    should not be allowed, and the post() method to handle the deletion of a request.
    """

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        return HttpResponseNotAllowed('[POST, DELETE]]', status=405,
                                      content=b'Method Not Allowed')

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        try:
            request_instance = get_object_or_404(Request, pk=pk)
            request_instance.delete()
            messages.success(request, "Request deleted successfully. ")
            return redirect('view_requests')
        except (Http404, Exception) as e:  # Handle unexpected exceptions
            messages.error(request, f'There was an error deleting this request: {str(e)}')
            return redirect('view_requests')

    def dispatch(self, wsgi_request, *args, **kwargs):
        if not wsgi_request.user.is_authenticated:
            return self.handle_no_permission()

        pk = kwargs.get('pk') or wsgi_request.POST.get('pk')
        try:
            instance = get_object_or_404(Request, pk=pk)
            if wsgi_request.user.is_tutor or (
                    wsgi_request.user.is_student and wsgi_request.user.id != instance.student.id):
                return render(wsgi_request, 'permission_denied.html', status=403)
        except Http404:
            pass
        
        return super().dispatch(wsgi_request, *args, **kwargs)


class ConfirmDeleteRequestView(LoginRequiredMixin, View):
    """ Class to represent confirming the deletion of a request

    This class is used as a view for the website. This class defines the get() method to confirm that the user is sure that
    they want to delete the request, and the post() method handles the deletion of a request.
    get_request_instance() is a helper method used to retrieve a request object.
    """

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        request_instance = get_object_or_404(Request, pk=pk)
        return render(request, 'confirm_delete_request.html', {'request_instance': request_instance})

    def post(self, request, pk):
        request_instance = get_object_or_404(Request, pk=pk)
        request_instance.delete()
        return redirect('view_requests')

    def dispatch(self, wsgi_request, *args, **kwargs):
        if not wsgi_request.user.is_authenticated:
            return self.handle_no_permission()

        pk = kwargs.get('pk') or wsgi_request.POST.get('pk')
        instance = get_object_or_404(Request, pk=pk)
        if wsgi_request.user.is_tutor or (wsgi_request.user.is_student and wsgi_request.user.id != instance.student.id):
            return render(wsgi_request, 'permission_denied.html', status=403)
        return super().dispatch(wsgi_request, *args, **kwargs)
