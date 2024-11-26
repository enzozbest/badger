# admin_functions/helpers/mixins.py
class SortingMixin:
    """
    A mixin to add sorting functionality to Django views.
    """
    valid_sort_fields = []
    default_sort_field = 'pk'

    def get_sorting_queryset(self, queryset):
        sort_field = self.request.GET.get('sort', self.default_sort_field)

        if not self.is_valid_sort_field(sort_field):
            sort_field = self.default_sort_field

        try:
            return queryset.order_by(sort_field)
        except Exception as e:
            print(f"Sorting error: {e}")
            return queryset.order_by(self.default_sort_field)

    def is_valid_sort_field(self, field):
        return field in self.valid_sort_fields or field.lstrip('-') in self.valid_sort_fields
