from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, render

from invoicer.models import Invoice


@login_required
def set_payment_status(http_request: HttpRequest, invoice_id: str, payment_status: int) -> HttpResponse:
    """Function that allows Admin users to update the payment status of an invoice.

    As this alters the server's state, only POST, PUT, and PATCH requests are allowed. All other methods are not allowed.
    :param http_request: the HTTP request object
    :param invoice_id: the id of the invoice to update
    :param payment_status: the new payment status of the invoice.
    :return: an appropriate HTTP response
    """
    user = http_request.user
    if not user.is_admin:
        return HttpResponse("You must be an admin to view this page", status=403)

    if http_request.method != "POST" and http_request.method != "PUT" and http_request.method != "PATCH":
        return HttpResponseNotAllowed(["POST, PUT, PATCH"], status=405, content=b"Only POST, PUT, and PATCH allowed")

    invoice = get_object_or_404(Invoice, invoice_id=invoice_id)
    invoice.payment_status = bool(payment_status)
    invoice.save()
    return render(http_request, 'payment_status_updated.html', status=200)
