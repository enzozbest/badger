from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponse
from .forms import RequestForm
from django.shortcuts import redirect
from request_handler.models import Request

from django.contrib import messages

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

def view_requests(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect('log_in')
    try:
        #Change to filter
        context = {'requests':list(Request.objects.filter(student = request.user))}
        print(context)
    except Request.DoesNotExist:
        context = {'requests':"You have no current requests"}

    return render(request,'view_requests.html',context )

def delete_request(request, pk):
    if not request.user.is_authenticated:
        return redirect('log_in')
    try:
        request_instance = get_object_or_404(Request, pk=pk, student=request.user)
        request_instance.delete()
        messages.success(request, "Request deleted successfully. ")
        return redirect('view_requests')
    except Request.DoesNotExist:
        messages.error(request, "Request cannot be found or deleted. ")
        return redirect('view_requests')
    except Exception as e: # handle unexpected exceptions
        messages.error(request, f'There was an error deleting this request: {str(e)}')
        return redirect('view_requests')

def confirm_delete_request(request, pk):
    request_instance = get_object_or_404(Request, pk=pk)
    if request.method == "POST":
        request_instance.delete()
        return redirect('view_requests')
    return render(request, 'confirm_delete_request.html', {'request_instance': request_instance})