from faker.providers import BaseProvider
from request_handler.models import Venue

class VenueProvider(BaseProvider):
    def venue(self):
        venues = list(Venue.objects.all())
        samples= self.random_sample(venues)
        ret = [sample.id for sample in samples]
        return ret