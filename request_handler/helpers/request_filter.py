import django_filters
from django.db.models import Q
from request_handler.models import Request

class AllocationFilter(django_filters.FilterSet):
    allocated = django_filters.BooleanFilter(
        label="Allocation Status",
        field_name="allocated",
        method="filter_allocated",
    )

    search = django_filters.CharFilter(
        method='filter_search',
        label="Search"
    )

    def filter_allocated(self, queryset, name, value):
        return queryset.filter(allocated=value)


    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(student__first_name__icontains=value) |
            Q(student__last_name__icontains=value) |
            Q(knowledge_area__icontains=value) |
            Q(allocated__icontains=value)
        )

    class Meta:
        model = Request
        fields = ['allocated', 'search']