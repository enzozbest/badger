from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from request_handler.forms import RejectRequestForm
from request_handler.models.request_model import Request


def reject_request(request, request_id):
    """Method that allows Admin users to reject a student's request and supply a reason for this rejection."""

    if request.user.user_type != "Admin":
        return HttpResponseForbidden("You do not have permission to reject this request.")
    req = get_object_or_404(Request, id=request_id)

    if request.method == 'POST':
        form = RejectRequestForm(request.POST)
        if form.is_valid():
            req.rejected_request = True
            req.rejection_reason = form.cleaned_data['reason']
            req.group_request_id = -1
            req.save()
            return redirect('view_requests')
    else:
        form = RejectRequestForm()

    return render(request, 'reject_request.html', {'form': form, 'request': req})
