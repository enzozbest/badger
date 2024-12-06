import os

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from invoicer.models import Invoice
from request_handler.models import Request
from django.conf import settings
from admin_functions.helpers.calculate_cost import calculate_num_lessons
from io import BytesIO
from code_tutors.aws import s3
from code_tutors.aws.resources import yaml_loader

LOCAL_STORE = not settings.USE_AWS_S3
LOGO_PATH = settings.LOGO_PATH
OUTPUT_PATH = settings.INVOICE_OUTPUT_PATH

def generate_invoice(request_obj: Request) -> None:
    LOCAL_STORE = not settings.USE_AWS_S3
    invoice: Invoice = request_obj.invoice
    buffer = BytesIO() #!!DO NOT REMOVE!!
    path = f'{OUTPUT_PATH}/{invoice.invoice_id}.pdf'

    if not LOCAL_STORE:
        pdf = canvas.Canvas(buffer, pagesize=A4)
    else:
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
        pdf = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4
    
    # Header Section
    pdf.drawImage(
        LOGO_PATH, 
        x=(width / 2) - 50, 
        y=height - 100, 
        width=100, 
        height=50, 
        preserveAspectRatio=True, 
        mask='auto'
    )
    # Add title
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(150, height - 60, "Invoice")

     # Recipient Information Section
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(20, height - 170, "Recipient Information:")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(40, height - 190, f"Recipient: {request_obj.student.full_name}")
    pdf.drawString(40, height - 210, f"Tutor: {request_obj.tutor.full_name}")
    pdf.drawString(40, height - 230, f"Tutor Email: {request_obj.tutor.email}")

    # Lesson Details Section
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(20, height - 260, "Lesson Details:")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(40, height - 280, f"Hourly Rate: £{request_obj.tutor.hourly_rate:.2f}")
    pdf.drawString(40, height - 300, f"Lessons Booked: {calculate_num_lessons(request_obj.frequency)}")
    pdf.drawString(40, height - 320, f"Total Cost: £{invoice.total:.2f}")

    # Footer Section
    pdf.setFont("Helvetica", 10)
    pdf.setFillColorRGB(0.5, 0.5, 0.5)  # Light gray for footer text
    pdf.drawCentredString(width / 2, 50, "Thank you for using our service!")
    pdf.setFillColorRGB(0, 0, 0)  # Reset to black for remaining content

    # # Add payment information
    # pdf.setFont("Helvetica-Bold", 12)
    # pdf.drawString(20, height - 260, "Payment Information:")
    # pdf.setFont("Helvetica", 12)
    # pdf.drawString(20, height - 280, f"Bank Name: {bank_details['bank_name']}")
    # pdf.drawString(20, height - 300, f"Account Number: {bank_details['account_number']}")
    # pdf.drawString(20, height - 320, f"Sort Code: {bank_details['sort_code']}")
    # pdf.drawString(20, height - 340, f"Reference: {bank_details['reference']}")

    # Finalize the PDF !!DO NOT REMOVE!!
    pdf.save()

    if not LOCAL_STORE:
        buffer.seek(0)
        s3.upload(obj=buffer, bucket=yaml_loader.get_bucket_name('invoicer'), key=f'invoices/pdfs/{invoice.invoice_id}.pdf')
    else:
        with open(path, "wb") as f:
            f.write(buffer.getvalue())

    buffer.close() #!!DO NOT REMOVE!!