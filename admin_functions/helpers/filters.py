import django_filters
from user_system.models import User

class UserFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = ['user_type']