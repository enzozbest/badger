import django_filters
from django.db.models import Q

from user_system.models import User


class UserFilter(django_filters.FilterSet):
    """Class to represent a filter that can be used in other parts of the code to filter Users by some characteristic.

    By default, this class will assume a "name" searching functionality, which includes partial matches, and a filter based
    on the user's account (user) type.
    """

    search = django_filters.CharFilter(
        method='filter_search',
        label="Search"
    )

    def filter_search(self, queryset, name, value):
        parts = value.split()
        if len(parts) < 2:
            return queryset.filter(
                Q(first_name__istartswith=parts[0]) |
                Q(last_name__istartswith=parts[0])
            )
        else:
            return queryset.filter(
                Q(first_name__istartswith=parts[0]) & Q(last_name__istartswith=parts[1])
            )

    class Meta:
        model = User
        fields = ['user_type', 'search']
