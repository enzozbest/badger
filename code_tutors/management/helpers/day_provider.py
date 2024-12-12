from faker.providers import BaseProvider
from user_system.models.day_model import Day


class DayProvider(BaseProvider):
    def days(self):
        days_list = list(Day.objects.all())
        return self.random_element(days_list)