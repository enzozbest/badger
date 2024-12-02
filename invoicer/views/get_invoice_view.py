from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect

from code_tutors.aws import s3
from invoicer.helpers.generate_invoice_id import generate_invoice_id
from invoicer.models import Invoice, get_latest_id_number


@login_required
def get_invoice(http_request: HttpRequest, invoice_id: str) -> HttpResponse | FileResponse:
    """View function to access an existing invoice.

    Upon request to this view function, an attempt is made to retrieve an invoice document as a PDF file. If this is
    stored locally, a FileResponse is returned. Otherwise, an appropriate HttpResponse is returned, redirecting the user
    to the location of the invoice.
    Admins can see all invoices for all students, Students can only see their own invoices, Tutors cannot see any invoices.
    :param http_request: the HTTP request object.
    :param invoice_id: the ID of the invoice to be retrieved.
    :return: Either the invoice file (if stored locally) or a redirection to the location of the invoice (if stored remotely).
    """
    user = http_request.user
    if user.is_tutor:
        return HttpResponse('You cannot view invoices as a tutor', status=403)

    invoice = get_object_or_404(Invoice, invoice_id=invoice_id)

    if not (user.is_admin or invoice.student == http_request.user):
        return HttpResponse('You cannot view this invoice!', status=403)

    if settings.USE_AWS_S3:
        key = f'invoices/pdfs/{invoice.invoice_id}.pdf'
        url = s3.generate_access_url(key=key, expiration=60)
        return redirect(url, permanent=True)
    else:
        return FileResponse(open(
            f'{settings.INVOICE_OUTPUT_PATH}/{generate_invoice_id(invoice.student, get_latest_id_number(invoice.student))}.pdf',
            'rb')
            , as_attachment=True, filename=f'{invoice.invoice_id}.pdf', status=200)
