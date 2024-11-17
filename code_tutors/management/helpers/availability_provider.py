from faker.providers import BaseProvider
from request_handler.models import Day

class AvailabilityProvider(BaseProvider):
    def availability(self):
        days = list(Day.objects.all())
        samples= self.random_sample(days)
        ret = [sample.id for sample in samples]
        return ret