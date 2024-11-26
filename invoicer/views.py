from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.conf import settings
from request_handler.models import Request
from invoicer.models import Invoice, get_latest_id_number
from invoicer.helpers.generate_invoice_id import generate_invoice_id
from invoicer.helpers import invoice_generator as ig
from admin_functions.helpers.calculate_cost import calculate_cost
from user_system.models import User

LOCAL_STORE = not settings.USE_AWS_S3

@login_required(login_url=settings.LOGIN_URL)
def generate_invoice_for_request(http_request: HttpRequest, request_id: int) -> HttpResponse:
    request_obj = Request.objects.get(id=request_id)

    if request_obj.invoice is not None:
        return HttpResponse(f"Invoice already generated. "
                            f"Found at: {request_obj.invoice.location if LOCAL_STORE else f'AWS S3 at invoices/pdfs/{request_obj.invoice_id}.pdf'} ", status=204)
    student = request_obj.student
    invoice_id = generate_invoice_id(student, get_latest_id_number(student))
    total_cost = calculate_cost(tutor=request_obj.tutor, request_id=request_obj.id)

    invoice = create_invoice_object(student=student, invoice_id=invoice_id, total_cost=total_cost)
    request_obj.invoice = invoice
    request_obj.save()
    ig.generate_invoice(request_obj)

    return HttpResponse(f"Invoice generated successfully!", status=201)



def create_invoice_object(student: User, invoice_id:str, total_cost: float) -> Invoice:
    if LOCAL_STORE:
        return Invoice.objects.create(invoice_id=invoice_id,
                                        student=student,
                                        total=total_cost,
                                         location=f'invoicer/pdfs/{invoice_id}.pdf')
    else:
        return Invoice.objects.create(invoice_id=invoice_id,
                                         student=student,
                                         total=total_cost)

