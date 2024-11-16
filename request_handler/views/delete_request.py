from django.views import View
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render, get_object_or_404
from request_handler.models import Request
from django.contrib import messages
from django.http import Http404


class DeleteRequestView(View):
    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        return HttpResponseBadRequest('This URL does not accept GET requests!')

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        if not request.user.is_authenticated:
            return redirect('log_in')
        try:
            request_instance = get_object_or_404(Request, pk=pk, student=request.user)
            request_instance.delete()
            messages.success(request, "Request deleted successfully. ")
            return redirect('view_requests')
        except (Http404, Exception) as e:  # Handle unexpected exceptions
            messages.error(request, f'There was an error deleting this request: {str(e)}')
            return redirect('view_requests')

class ConfirmDeleteRequestView(View):
    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        request_instance = self.get_request_instance(pk)
        return render(request, 'confirm_delete_request.html', {'request_instance': request_instance})

    def post(self, request, pk):
        request_instance = self.get_request_instance(pk)
        request_instance.delete()
        return redirect('view_requests')

    def get_request_instance(self, pk: int) -> Request:
        return get_object_or_404(Request, pk=pk)