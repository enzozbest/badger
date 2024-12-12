from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from admin_functions.helpers.calculate_cost import calculate_cost
from invoicer.helpers import invoice_generator as ig
from invoicer.helpers.generate_invoice_id import generate_invoice_id
from invoicer.models import Invoice, get_latest_id_number
from request_handler.models.request_model import Request
from user_system.models.user_model import User

LOCAL_STORE = not settings.USE_AWS_S3
OUTPUT_PATH = settings.INVOICE_OUTPUT_PATH


@login_required(login_url=settings.LOGIN_URL)
def generate_invoice_for_request(http_request: HttpRequest, tutoring_request_id: int) -> HttpResponse:
    """View function for generating an invoice for a request

    :param http_request: the HTTP request
    :param tutoring_request_id: the tutoring request id
    :return: an appropriate HTTP response.
    """

    if http_request.user.user_type == User.ACCOUNT_TYPE_STUDENT or http_request.user.user_type == User.ACCOUNT_TYPE_TUTOR:
        return render(http_request, 'permission_denied.html', status=403)

    request_obj = Request.objects.get(id=tutoring_request_id)

    if request_obj.invoice is not None:
        LOCAL_STORE = not settings.USE_AWS_S3
        return render(http_request, 'invoice_already_generated.html', {
            "path": f"{OUTPUT_PATH / f'{request_obj.invoice_id}' if LOCAL_STORE else f'AWS S3 at invoices/pdfs/{request_obj.invoice_id}.pdf'}"},
                      status=409)

    # Get necessary parameters for invoice generation:
    student = request_obj.student
    invoice_id = generate_invoice_id(student, get_latest_id_number(student))
    total_cost = calculate_cost(tutor=request_obj.tutor, request_id=request_obj.id)

    # Generate the invoice and save the created object.
    invoice = create_invoice_object(student=student, invoice_id=invoice_id, total_cost=total_cost)
    invoice.save()

    # Update the request object
    request_obj.invoice = invoice
    request_obj.save()
    ig.generate_invoice(request_obj)

    return render(http_request, 'invoice_generated.html', status=201)

def create_invoice_object(student: User, invoice_id: str, total_cost: float) -> Invoice:
    return Invoice.objects.create(invoice_id=invoice_id,
                                  student=student,
                                  total=total_cost)
