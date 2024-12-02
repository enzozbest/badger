from random import randint

from django.core.management.base import BaseCommand
from faker import Faker

from admin_functions.views.allocate_requests import _allocate, _get_tuple, _update_availabilities
from code_tutors.management.helpers import programming_langs_provider, term_provider, user_provider, venue_provider
from request_handler.models import Request


class Command(BaseCommand):
    REQUEST_COUNT = 100

    def __init__(self):
        self.faker = Faker('en_GB')
        self.faker.add_provider(programming_langs_provider.ProgrammingLangsProvider)
        self.faker.add_provider(term_provider.TermProvider)
        self.faker.add_provider(user_provider.UserProvider)
        self.faker.add_provider(venue_provider.VenueProvider)
        self.frequencies = ['Weekly', 'Fortnightly', 'Biweekly']

    def handle(self, *args, **options):
        self.__init__()
        self.create_requests()
        self.requests = Request.objects.all()

    def create_requests(self):
        request_count = Request.objects.count()
        while request_count < self.REQUEST_COUNT:
            print(f'Seeding request {request_count}/{self.REQUEST_COUNT}', end='\r')
            self.generate_request()
            request_count = Request.objects.count()
        print('Request seeding complete. \n')

    def generate_request(self):
        student = self.faker.student()
        if not student:
            print("No valid student found. Skipping this request.")
            return
        allocated = False if randint(0, 1) else True
        tutor = None
        knowledge_area = self.faker.programming_langs()
        term = self.faker.term()
        frequency = self.frequencies[randint(0, 2)]
        duration = str(randint(1, 3)) + 'h'
        venue_preference = self.faker.venue()
        recurring = True if randint(0, 1) else False
        self.try_create_request(
            {'knowledge_area': knowledge_area, 'term': term, 'frequency': frequency, 'duration': duration,
             'student': student, 'tutor': tutor, 'allocated': allocated,
             'venue_preference': venue_preference, 'is_recurring': recurring})

    def try_create_request(self, data):
        try:
            self.create_request(data)
        except Exception as e:
            print(e)

    def create_request(self, data):
        req_object = Request.objects.create(
            student=data['student'],
            allocated=data['allocated'],
            tutor=data['tutor'],
            knowledge_area=data['knowledge_area'],
            term=data['term'],
            frequency=data['frequency'],
            duration=data['duration'],
        )
        if data['venue_preference'] and isinstance(data['venue_preference'], list):
            req_object.venue_preference.set(data['venue_preference'])

        if data['allocated']:
            lesson_request, suitable_tutors, venues = _get_tuple(req_object.id)
            day = None
            if req_object.student.availability.exists():
                day = req_object.student.availability.all()[0]
            else:
                req_object.allocated = False

            if suitable_tutors.exists() and len(suitable_tutors.all()) > 0 and req_object.allocated:
                _allocate(req_object, suitable_tutors.all()[0], venues[0], day)
                _update_availabilities(req_object, day)
            else:
                req_object.allocated = False
            req_object.save()

        req_object.save()
