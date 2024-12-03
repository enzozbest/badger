from django.db import models
from django.test import TestCase

from admin_functions.helpers.mixins import SortingMixin


class DummyModel(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()


class DummyView(SortingMixin):
    def __init__(self):
        self.valid_sort_fields = ['name', 'age']
        self.default_sort_field = 'name'
        self.request = None


class SortingMixinTest(TestCase):
    def setUp(self):
        self.view = DummyView()
        DummyModel.objects.create(name="Alice", age=30)
        DummyModel.objects.create(name="Bob", age=25)

    def test_get_sorting_queryset_with_invalid_field(self):
        self.view.request = self.client.get('/', {'sort': 'invalid_field'}).wsgi_request
        queryset = DummyModel.objects.all()
        result = self.view.get_sorting_queryset(queryset)
        self.assertQuerysetEqual(result, queryset.order_by(self.view.default_sort_field))

    def test_is_string_field_invalid_field_name(self):
        result = self.view.is_string_field('invalid_field', DummyModel)
        self.assertFalse(result)
