from django.core.exceptions import ValidationError
from django.test import TestCase
from request_handler.models import Request

class RequestModelTest(TestCase):
    def setUp(self):
        self.model = Request.objects.create()

    def test_request_is_valid(self):
        self.assertTrue(self.model.is_valid())

    def test_empty_request(self):
        self.assertRaises(ValidationError, self.model.is_valid)