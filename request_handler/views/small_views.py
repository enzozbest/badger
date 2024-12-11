from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def request_success(request: HttpRequest) -> HttpResponse:
    """Function based view to redirect a user to a success screen.

    Usually called as an accompaniment to a 200 OK response.
    :param request: the HTTP request object
    :return: an appropriate HTTP response
    """
    return render(request, 'request_success.html')

def permission_denied(request: HttpRequest) -> HttpResponse:
    """Function based view to redirect a user to a denied page.

    Usually called as an accompaniment to a 403 Forbidden response.
    :param request: the HTTP request object
    :return: an appropriate HTTP response
    """
    return render(request, 'permission_denied.html', status=403)

def processing_late_request(request: HttpRequest) -> HttpResponse:
    """Function based view to redirect a user to a processing late tutoring request page.

    :param request: the HTTP request object
    :return: an appropriate HTTP response
    """
    return render(request, 'processing_late_request.html')
