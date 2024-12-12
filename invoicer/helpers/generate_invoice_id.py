from user_system.models.user_model import User


def generate_invoice_id(student: User, latest_number: str) -> str:
    """Function to generate an invoice id for a given student.

    Invoice IDs take the form XXXYYY-00, where XXX are the 3 first letters of the student's first name, YYY are the 3 first
    letters of the student's last name, and the number at the end corresponds with the number of their invoice.

    :param student: the Student user for whom an invoice is being generated.
    :param latest_number: the last invoice number for this student.
    :return: the generated invoice id.
    """
    return f'INV-{student.first_name[0:3:1].upper()}{student.last_name[0:3:1].upper()}-{int(latest_number if latest_number else "0") + 1}'
