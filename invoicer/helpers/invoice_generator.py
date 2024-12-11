import os
from io import BytesIO

from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from admin_functions.helpers.calculate_cost import calculate_num_lessons
from code_tutors.aws import s3
from code_tutors.aws.resources import yaml_loader
from invoicer.models import Invoice
from request_handler.models import Request

_LOGO_PATH = settings.LOGO_PATH
_OUTPUT_PATH = settings.INVOICE_OUTPUT_PATH


def draw_invoice(pdf: canvas.Canvas, request_obj: Request, invoice: Invoice) -> None:
    """Draw the invoice header with the logo and title."""
    width, height = A4
    pdf.drawImage(_LOGO_PATH, x=20, y=height - 100, width=100, height=50, preserveAspectRatio=True, mask='auto')

    # Add title
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(150, height - 60, "Invoice")

    # Add recipient details
    pdf.setFont("Helvetica", 12)
    pdf.drawString(20, height - 120, f"Recipient: {request_obj.student.full_name}")
    pdf.drawString(20, height - 140, f"Tutor: {request_obj.tutor.full_name}")

    # Add lesson details
    pdf.drawString(20, height - 180, f"Hourly Rate: £{request_obj.tutor.hourly_rate:.2f}")
    pdf.drawString(20, height - 200, f"Lessons Booked: {calculate_num_lessons(request_obj.frequency)}")
    pdf.drawString(20, height - 220, f"Total Cost: £{invoice.total:.2f}")


def save_or_upload_pdf(buffer: BytesIO, invoice: Invoice, path: str):
    """ Save the invoice pdf in local storeage or in AWS S3, depending on settings.py configurations """
    if settings.USE_AWS_S3:
        buffer.seek(0)
        s3.upload(obj=buffer, bucket=yaml_loader.get_bucket_name('invoicer'),
                  key=f'invoices/pdfs/{invoice.invoice_id}.pdf')
    else:
        with open(path, "wb") as f:
            f.write(buffer.getvalue())


def generate_invoice(request_obj: Request) -> None:
    """Function that automatically generates a formatted PDF file for an invoice.

    This function uses reportlab to generate the PDF. If _LOCAL_STORE is set, the PDF is stored in the local machine,
    at invoicer/invoices/pdfs. Otherwise, the PDF is automatically uploaded to Amazon's S3 based on the configuration set
    in the code_tutors.aws module.
    :param request_obj: the tutoring request object for which an invoice is being generated.
    """
    invoice: Invoice = request_obj.invoice
    buffer = BytesIO()  # !!DO NOT REMOVE!!
    path = f'{_OUTPUT_PATH}/{invoice.invoice_id}.pdf'

    if not settings.USE_AWS_S3:
        pdf = canvas.Canvas(buffer, pagesize=A4)
    else:
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
        pdf = canvas.Canvas(buffer, pagesize=A4)

    draw_invoice(pdf, request_obj, invoice)

    # Finalize the PDF !!DO NOT REMOVE!!
    pdf.save()

    save_or_upload_pdf(buffer, invoice, path)

    buffer.close()  # !!DO NOT REMOVE!!
