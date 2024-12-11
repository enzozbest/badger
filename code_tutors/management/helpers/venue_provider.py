from faker.providers import BaseProvider

from request_handler.models.venue_model import Venue

Venue


class VenueProvider(BaseProvider):
    def venue(self):
        venues = list(Venue.objects.all())
        samples = self.random_sample(venues)
        ret = [sample.id for sample in samples]
        return ret
