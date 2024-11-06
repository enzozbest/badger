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
                request_instance = form.save(commit=False)
                request_instance.student = request.user
                request_instance.save()

                #Manually add selected days to Request instance, as the automatic method is not working.
                for day in form.cleaned_data['available_days']:
                    request_instance.availability.add(day)

                return redirect('request_success')
            except Exception as e:
                form.add_error(error=f'There was an error submitting this form! {e}', field='term')
    else:
        form = RequestForm()
    return render(request, 'create_request.html', {'form': form})

def request_success(request: HttpRequest) -> HttpResponse:
    return render(request, 'request_success.html')