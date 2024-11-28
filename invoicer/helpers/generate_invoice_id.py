from user_system.models import User

def generate_invoice_id(student: User, latest_number: int) -> str:
    return f'INV-{student.first_name[0:3:1].upper()}{student.last_name[0:3:1].upper()}-{int(latest_number if latest_number else "0") + 1}'
