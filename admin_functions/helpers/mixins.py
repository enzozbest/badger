from django.core.exceptions import FieldDoesNotExist
from django.db.models.functions import Upper


class SortingMixin:
    """Class to represent a Mixin for ListViews that allows users to sort the list based on some fields

    The fields by which a list can be sorted must be set in the class where the Mixin is used.
    By default, sorting uses the primary key of the elements in the list in ascending order.
    """
    
    valid_sort_fields = []
    default_sort_field = 'pk'

    def get_sorting_queryset(self, queryset):
        sort_field = self.determine_sort_field(self.request.GET.get('sort', self.default_sort_field))
        stripped = sort_field.lstrip('-')

        # If the field is not a string, we do not need to worry about upper and lowercase characters
        if not self.is_string_field(stripped, queryset.model):
            return queryset.order_by(sort_field)

        ordering = Upper(stripped).asc()
        if sort_field.startswith('-'):
            ordering = ordering.desc()
        return queryset.order_by(ordering)

    def determine_sort_field(self, field):
        stripped = field.lstrip('-')
        return field if (stripped in self.valid_sort_fields) else self.default_sort_field

    def is_string_field(self, field_name, model):
        try:
            field = model._meta.get_field(field_name)
            return field.get_internal_type() in ['CharField', 'TextField']
        except FieldDoesNotExist:
            return False
