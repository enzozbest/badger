from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph

def generate_invoice(file_name: str, company_info, recipient_info, invoice_data):
    pdf = SimpleDocTemplate(file_name, pagesize=A4)
    elements = []


    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]
    normal_style = styles["Normal"]

    elements.append(Paragraph(company_info['name'], title_style))
    elements.append(Paragraph(company_info['address'], normal_style))
    elements.append(Paragraph(f'Phone: {company_info["phone"]}', normal_style))
    elements.append(Paragraph(f'email: {company_info["email"]}', normal_style))
    elements.append(Paragraph("<br></br>", normal_style))

    elements.append(Paragraph(f'Billed to: {recipient_info["name"]}', normal_style))
    elements.append(Paragraph(f'Address: {recipient_info["address"]}', normal_style))
    elements.append(Paragraph(f'Phone: {recipient_info["phone"]}', normal_style))
    elements.append(Paragraph(f'Email: {recipient_info["email"]}', normal_style))
    elements.append(Paragraph("<br></br>", normal_style))

    elements.append(Paragraph(f'Invoice Number: {invoice_data["number"]}', normal_style))
    elements.append(Paragraph(f'Invoice Date: {invoice_data["date"]}', normal_style))
    elements.append(Paragraph("<br></br>", normal_style))

    table_data = [['Description', 'Quantity', 'Unit Price', 'Total']]
    for item in invoice_data["items"]:
        table_data.append([item["description"], item["quantity"], f'£{item["unit_price"]:.2f}', f'{item["total"]:.2f}'])

    table_data.append(["", "", "Total", f'£{invoice_data["total"]:.2f}'])

    table = Table(table_data, colWidths=[250, 100, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)
    elements.append(Paragraph("<br/><br/> Thank you for your business!", normal_style))

    pdf.build(elements)


def test():
    company_info = {
        "name": "CodeConnect by CodeTutors",
        "address": "123 Nowhere, London, A1 1AB",
        "email": "test@example.org",
        "phone": "0123456789",
    }
    recipient_info = {
        "name": "John Doe",
        "address": "123 Nowhere, London, A1 1AB",
        "email": "jd@example.org",
        "phone": "0123456789",
    }
    invoice_data = {
        "number": "123456789",
        "date": "2020-01-10",
        "items": [
            {
                "description": "test1",
                "quantity": 2,
                "unit_price": 500,
                "total": 1000,
            },
            {
                "description": "test2",
                "quantity": 1,
                "unit_price": 200,
                "total": 200,
            }
        ],
        "total": 300
    }

    generate_invoice("invoice.pdf", company_info, recipient_info, invoice_data)