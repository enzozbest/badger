import django_filters
from tutorials.models import User

class UserFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = ['user_type']