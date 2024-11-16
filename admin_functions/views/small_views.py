from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render, redirect


def admin_dash(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect('log_in')

    if request.user.user_type != 'Admin':
        return render(request, 'permission_denied.html', status=403)

    if request.method == 'POST':
        return HttpResponseNotAllowed("This URL only accepts GET requests.", status=405, content=b'Not Allowed')

    return render(request, 'admin_dashboard.html')