import django_filters
from django.db.models import Q

from calendar_scheduler.models import Booking


class CancellationRequestFilter(django_filters.FilterSet):

    search = django_filters.CharFilter(
        method='filter_search',
        label="Search"
    )

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(id__icontains=value) |
            Q(student__first_name__icontains=value) |
            Q(tutor__first_name__icontains=value) |
            Q(date__icontains=value)
        )
        

    class Meta:
        model = Booking
        fields = ['search']
