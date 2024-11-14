from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

def request_success(request: HttpRequest) -> HttpResponse:
    return render(request, 'request_success.html')

def permission_denied(request: HttpRequest) -> HttpResponse:
    return render(request, 'permission_denied.html', status=403)

def processing_late_request(request: HttpRequest) -> HttpResponse:
    return render(request, 'processing_late_request.html' )

    
