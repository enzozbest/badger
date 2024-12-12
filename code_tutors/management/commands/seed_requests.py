from random import randint

from django.core.management.base import BaseCommand
from faker import Faker

from admin_functions.views.allocate_requests import _allocate, _update_availabilities, get_suitable_tutors, \
    get_venue_preference
from code_tutors.management.helpers import programming_langs_provider, term_provider, user_provider, venue_provider
from request_handler.fixtures.create_test_requests import create_test_requests
from request_handler.models.request_model import Request


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
        create_test_requests()
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
            group_id = Request.objects.count()
            if not data['is_recurring']:
                self.create_request(data, group_id, data['term'])
            else:
                term = data['term']
                self.create_request(data, group_id, term)
                if term == "September":
                    term = "January"
                    self.create_request(data, group_id, term)
                if term == "January":
                    term = "May"
                    self.create_request(data, group_id, term)                
        except Exception as e:
            pass

    def create_request(self, data, id, request_term):
        req_object = Request.objects.create(
            student=data['student'],
            allocated=data['allocated'],
            tutor=data['tutor'],
            knowledge_area=data['knowledge_area'],
            term=request_term,
            frequency=data['frequency'],
            duration=data['duration'],
            group_request_id=id,
            is_recurring=data['is_recurring']
        )
        if data['venue_preference'] and isinstance(data['venue_preference'], list):
            req_object.venue_preference.set(data['venue_preference'])

        if data['allocated']:
            venues = get_venue_preference(req_object.venue_preference)

            if req_object.student.availability.exists():
                day1 = req_object.student.availability.all()[0]
                try:
                    day2 = req_object.student.availability.all()[1] if req_object.frequency == 'Biweekly' else None
                except IndexError:
                    req_object.allocated = False
                    req_object.save()
                    raise Exception("Skipping this user, no availability for Biweekly allocation!")
            else:
                req_object.allocated = False
                req_object.save()
                return

            req_object.refresh_from_db()
            suitable_tutors = get_suitable_tutors(req_object.id, day1.id, day2.id if day2 else None)

            if suitable_tutors.exists() and len(suitable_tutors.all()) > 0 and req_object.allocated:
                _allocate(req_object, suitable_tutors.all()[0], venues[0], day1, day2)
                _update_availabilities(req_object, day1, day2)
            else:
                req_object.allocated = False

            req_object.save()

        req_object.save()
