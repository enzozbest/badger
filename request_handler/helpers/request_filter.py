import django_filters
from django.db.models import Q

from request_handler.models import Request


class RequestFilter(django_filters.FilterSet):
    """Class to represent a filter that can be used to add filter and search functionality to ListViews.

    Requests can be filtered by their allocation status only.
    Requests can be searched by either: student first name, student last name, knowledge area, or allocation status. All
    of those include partial matches.
    """
    
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
