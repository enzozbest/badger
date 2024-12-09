import django_filters
from django.db.models import Q
from datetime import datetime
from calendar_scheduler.models import Booking

class CancellationRequestFilter(django_filters.FilterSet):

    search = django_filters.CharFilter(
        method='filter_search',
        label="Search"
    )

    def filter_search(self, queryset, name, value):
        search_filter = Q(student__first_name__icontains=value) | \
                        Q(tutor__first_name__icontains=value)

        if value:
            value_cleaned = value.replace('.', '').strip()

            try:
                if len(value_cleaned) == 3:
                    search_month = datetime.strptime(value_cleaned, "%b").month
                    search_filter |= Q(date__month=search_month)
                else:
                    search_date = datetime.strptime(value_cleaned, "%b %d")
                    search_filter |= Q(date__month=search_date.month, date__day__icontains=search_date.day)
            except ValueError:
                try:
                    search_day = int(value_cleaned)
                    search_filter |= Q(date__day__icontains=search_day)
                except ValueError:
                    pass

            try:
                search_year = int(value_cleaned)
                search_filter |= Q(date__year=search_year)
            except ValueError:
                pass

            try:
                search_filter |= Q(id__icontains=int(value_cleaned))
            except ValueError:
                pass

        return queryset.filter(search_filter)

    class Meta:
        model = Booking
        fields = ['search']