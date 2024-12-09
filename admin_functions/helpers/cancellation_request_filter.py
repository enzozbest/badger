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
        try:
            search_date = datetime.strptime(value, "%b. %d, %Y").date() 
            search_filter |= Q(date=search_date)
        except ValueError:
            try:
                search_date = datetime.strptime(value, "%b %d, %Y").date()
                search_filter |= Q(date=search_date)
            except ValueError:
                try:
                    search_date = datetime.strptime(value, "%b %d").date()
                    current_year = datetime.now().year
                    search_date = search_date.replace(year=current_year)
                    search_filter |= Q(date=search_date)
                except ValueError:
                    pass

        try:
            search_filter |= Q(id=int(value))
        except ValueError:
            pass
        
        return queryset.filter(search_filter)

    class Meta:
        model = Booking
        fields = ['search']
