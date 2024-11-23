from django.db import models
from user_system.models import User

class Invoice(models.Model):
    invoice_id = models.CharField(primary_key=True, unique=True, max_length=100)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_invoiced')
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        if not self.invoice_id:
            self.invoice_id = generate_invoice_id(self.student)
        super(Invoice, self).save(*args, **kwargs)


def generate_invoice_id(student: User) -> str:
    latest_number = Invoice.objects.filter(student=student).latest('invoice_id').invoice_id[0:2:-1]
    return f'INV-{student.first_name[0:2:1]}{student.last_name[0:2:1]}-{int(latest_number) + 1}'
