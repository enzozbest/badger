from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from user_system.helpers import login_prohibited


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    """Display the current user's dashboard."""
    current_user = request.user
    return render(request, 'dashboard.html', {'user': current_user})


@login_prohibited
def home(request: HttpRequest) -> HttpResponse:
    """Display the application's start/home screen."""
    return render(request, 'home.html')


def log_out(request):
    """Log out the current user"""

    logout(request)
    return redirect('home')
