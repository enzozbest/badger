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

_LOCAL_STORE = not settings.USE_AWS_S3
_LOGO_PATH = settings.LOGO_PATH
_OUTPUT_PATH = settings.INVOICE_OUTPUT_PATH


def generate_invoice(request_obj: Request) -> None:
    """Function that automatically generates a formatted PDF file for an invoice.

    This function uses reportlab to generate the PDF. If _LOCAL_STORE is set, the PDF is stored in the local machine,
    at invoicer/invoices/pdfs. Otherwise, the PDF is automatically uploaded to Amazon's S3 based on the configuration set
    in the code_tutors.aws module.
    :param request_obj: the tutoring request object for which an invoice is being generated.
    """
    LOCAL_STORE = not settings.USE_AWS_S3
    invoice: Invoice = request_obj.invoice
    buffer = BytesIO()  # !!DO NOT REMOVE!!
    path = f'{_OUTPUT_PATH}/{invoice.invoice_id}.pdf'

    if not LOCAL_STORE:
        pdf = canvas.Canvas(buffer, pagesize=A4)
    else:
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
        pdf = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4
    
    # Header with Logo
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(20, height - 60, "Code Connect Tutors")
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(width - 200, height - 60, "Transfer Confirmation")
    pdf.setFont("Helvetica", 10)

    pdf.setLineWidth(1)
    pdf.line(20 + 28, height - 90, width - 28, height - 90)
    
    content_start = height - 150

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(20, content_start, "Recipient details")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(40, content_start - 20, f"Tutor Name: {request_obj.tutor.full_name}")
    pdf.drawString(40, content_start - 40, f"Tutor Email: {request_obj.tutor.email}")
    
    # Student Details
    content_start -= 80
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(20, content_start, "Payer details")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(40, content_start - 20, f"Student Name: {request_obj.student.full_name}")
    
    # Transfer Overview
    content_start -= 80
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(20, content_start, "Transfer details")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(40, content_start - 20, f"Hourly Rate: £{request_obj.tutor.hourly_rate:.2f}")
    pdf.drawString(40, content_start - 40, f"Lessons Booked: {calculate_num_lessons(request_obj.frequency)}")
    pdf.drawString(40, content_start - 60, f"Total Cost: £{invoice.total:.2f}")
    pdf.drawString(40, content_start - 80, "Status: Completed")
    
    # Footer
    pdf.setFont("Helvetica", 8)
    pdf.setFillColorRGB(0.5, 0.5, 0.5)  # Light gray
    pdf.drawCentredString(width / 2, 50, "Thank you for using Code Connect Tutors!")
    pdf.drawCentredString(width / 2, 40, "For support, contact support@codeconnect.com")
    pdf.setFillColorRGB(0, 0, 0)  # Reset color

    pdf.save()

    if not LOCAL_STORE:
        buffer.seek(0)
        s3.upload(obj=buffer, bucket=yaml_loader.get_bucket_name('invoicer'),
                  key=f'invoices/pdfs/{invoice.invoice_id}.pdf')
    else:
        with open(path, "wb") as f:
            f.write(buffer.getvalue())

    buffer.close()  # !!DO NOT REMOVE!!
