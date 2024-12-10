from django.urls.conf import path

from .views.generate_invoice_view import generate_invoice_for_request
from .views.get_invoice_view import get_invoice
from .views.set_payment_status_view import set_payment_status

urlpatterns = [
    path("generate/<int:tutoring_request_id>/", generate_invoice_for_request, name="generate_invoice"),
    path("get/<str:invoice_id>/", get_invoice, name='get_invoice'),
    path("set/payment/status/<str:invoice_id>/<int:payment_status>", set_payment_status, name="set_payment_status"),
]
