from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse

from code_tutors.aws import s3
from invoicer.models import Invoice
from django.shortcuts import get_object_or_404, redirect


@login_required
def get_invoice(request: HttpRequest, invoice_id: str) -> HttpResponse:
    user = request.user
    if user.is_tutor:
        return HttpResponse('You cannot view invoices as a tutor', status=401)

    invoice = get_object_or_404(Invoice, invoice_id=invoice_id)
    key = f'invoices/pdfs/{invoice.invoice_id}.pdf'
    url = s3.generate_access_url(key=key)
    return redirect(url, permanent=True)
