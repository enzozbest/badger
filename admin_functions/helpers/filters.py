import django_filters

from request_handler.models import Request
from user_system.models import User

class UserFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = ['user_type']

class AllocationFilter(django_filters.FilterSet):
    class Meta:
        model = Request
        fields = ['allocated']