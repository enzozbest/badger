from django.db.models.functions import Upper

class SortingMixin:
    valid_sort_fields = []
    default_sort_field = 'pk'

    def get_sorting_queryset(self, queryset):
        sort_field = self.request.GET.get('sort', self.default_sort_field)

        if not self.is_valid_sort_field(sort_field):
            sort_field = self.default_sort_field

        try:
            if self.is_string_field(sort_field.lstrip('-'), queryset.model):
                ordering = Upper(sort_field.lstrip('-'))
                if sort_field.startswith('-'):
                    ordering = ordering.desc()
                return queryset.order_by(ordering)

            return queryset.order_by(sort_field)
        except Exception as e:
            print(f"Sorting error: {e}")
            return queryset.order_by(self.default_sort_field)

    def is_valid_sort_field(self, field):
        return field in self.valid_sort_fields or field.lstrip('-') in self.valid_sort_fields

    def is_string_field(self, field_name, model):
        try:
            field = model._meta.get_field(field_name)
            return field.get_internal_type() in ['CharField', 'TextField']
        except Exception:
            return False
