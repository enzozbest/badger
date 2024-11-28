from django.http import HttpResponse
from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from invoicer.models import Invoice


def set_payment_status(request: HttpRequest, invoice_id: str, payment_status: int) -> HttpResponse:
    user = request.user
    if not user.is_admin:
        return HttpResponse("You must be an admin to view this page", status=401)

    invoice = get_object_or_404(Invoice, invoice_id=invoice_id)
    invoice.payment_status = bool(payment_status)
    invoice.save()
    return HttpResponse("Payment status updated successfully", status=200)