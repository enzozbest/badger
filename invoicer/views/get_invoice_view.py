from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, FileResponse

from code_tutors.aws import s3
from invoicer.helpers.generate_invoice_id import generate_invoice_id
from invoicer.models import Invoice, get_latest_id_number
from django.shortcuts import get_object_or_404, redirect
from django.conf import settings

@login_required
def get_invoice(request: HttpRequest, invoice_id: str) -> HttpResponse | FileResponse:
    user = request.user
    if user.is_tutor:
        return HttpResponse('You cannot view invoices as a tutor', status=401)

    invoice = get_object_or_404(Invoice, invoice_id=invoice_id)
    if not (user.is_admin or invoice.student == request.user):
        return HttpResponse('You cannot view this invoice!', status=401)

    if settings.USE_AWS_S3:
        key = f'invoices/pdfs/{invoice.invoice_id}.pdf'
        url = s3.generate_access_url(key=key, expiration=60)
        return redirect(url, permanent=True)
    else:
        return FileResponse(open(f'{settings.INVOICE_OUTPUT_PATH}/{generate_invoice_id(invoice.student, get_latest_id_number(invoice.student))}.pdf', 'rb')
                            , as_attachment=True, filename=f'{invoice.invoice_id}.pdf', status=200)
