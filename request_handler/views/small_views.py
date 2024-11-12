from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

def request_success(request: HttpRequest) -> HttpResponse:
    return render(request, 'request_success.html')

def permission_denied(request: HttpRequest) -> HttpResponse:
    return render(request, 'permission_denied.html')