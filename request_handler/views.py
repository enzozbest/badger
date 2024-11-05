from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from .forms import RequestForm
from django.shortcuts import redirect

def create_request(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect('log_in')

    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                return redirect('request_success')
            except :
                form.add_error(error='There was an error submitting this form!', field='term')
    else:
        form = RequestForm()
    return render(request, 'create_request.html', {'form': form})

def request_success(request: HttpRequest) -> HttpResponse:
    return render(request, 'request_success.html')