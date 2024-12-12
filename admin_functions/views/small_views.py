from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render
from request_handler.models import Request


@login_required
def admin_dash(request: HttpRequest) -> HttpResponse:
    """ View function to display the Admin dashboard.

    Only Admin users can see this page, so all other user types will receive a 403 Forbidden error if trying to access.
    Because this is a read-only response, only GET requests are accepted.
    :param request: the HTTP request object.
    :return: an appropriately formatted HttpResponse.
    """
    if request.user.user_type != 'Admin':
        return render(request, 'permission_denied.html', status=403)

    if request.method == 'POST':
        return HttpResponseNotAllowed("[GET]", status=405, content=b'Not Allowed')
    
    # Count rejected allocations
    rejected_allocations_count = Request.objects.filter(rejected_request=True).count()
    allocated_without_invoices_count = Request.objects.filter(allocated=True, invoice__isnull=True).count()
    unallocated_requests_count = Request.objects.filter(allocated=False).count()

    context = {
        'rejected_allocations_count': rejected_allocations_count,
        'allocated_without_invoices_count': allocated_without_invoices_count,
        'unallocated_requests_count': unallocated_requests_count,
    }

    return render(request, 'admin_dashboard.html', context)
