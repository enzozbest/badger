from random import randint

from django.core.management.base import BaseCommand
from faker import Faker

from calendar_scheduler.models import Booking
from code_tutors.management.helpers import day_provider, programming_langs_provider, term_provider, user_provider, \
    venue_provider
from request_handler.models.venue_model import Venue
from request_handler.views.accept_request import get_first_weekday

from datetime import timedelta, datetime


class Command(BaseCommand):
    BOOKING_COUNT = 50

    def __init__(self):
        self.faker = Faker('en_GB')
        self.faker.add_provider(programming_langs_provider.ProgrammingLangsProvider)
        self.faker.add_provider(term_provider.TermProvider)
        self.faker.add_provider(user_provider.UserProvider)
        self.faker.add_provider(venue_provider.VenueProvider)
        self.faker.add_provider(day_provider.DayProvider)
        self.frequencies = ['Weekly', 'Fortnightly', 'Biweekly']
        self.bookings_count = 0
        self.lesson_identifier = 0
        self.date = None

    def handle(self, *args, **options):
        self.__init__()
        self.create_bookings()
        self.bookings = Booking.objects.all()

    def create_bookings(self):
        while self.bookings_count < self.BOOKING_COUNT:
            print(f'Seeding bookings {self.bookings_count}/{self.BOOKING_COUNT}', end='\r')
            self.generate_bookings()
            self.bookings_count += 1
            self.lesson_identifier += 1
        print('Booking seeding complete. \n')

    def generate_bookings(self):
        student = self.faker.student()
        if not student:
            print("No valid student found. Skipping this request.")
        tutor = self.faker.tutor()
        knowledge_area = self.faker.programming_langs()
        term = self.faker.term()
        duration = str(randint(1, 3)) + 'h'
        venue = Venue.objects.get(id=(self.faker.venue()[0]))
        day = self.faker.days()
        day2 = self.faker.days()
        if term == "September":
            self.date = get_first_weekday(2024, 9, day).date()
        elif term == 'January':
            self.date = get_first_weekday(2025, 1, day).date()
        else:
            self.date = get_first_weekday(2025, 5, day).date()

        title = f"Tutor session with {student.first_name} {student.last_name} and {tutor.first_name} {tutor.last_name}"
        recurring = True if randint(0, 1) else False
        self.try_create_bookings(
            {'knowledge_area': knowledge_area, 'term': term, 'duration': duration, 'student': student,
            'tutor': tutor, 'is_recurring': recurring, 'venue': venue, 'title': title, 'day': day, 'day2':day2
            })

    def determine_biweekly_date(self, day, day2):
        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day1 = weekdays.index(day)
        day2 = weekdays.index(day2)
        if self.date.weekday() == day1:
            # Find the difference from day1 to day2
            dayDiff = (day2 - day1 + 7) % 7
            self.date += timedelta(days=dayDiff)
            return
        else:
            # Find the difference from day2 to day1
            dayDiff = (day1 - self.date.weekday() + 7) % 7
            self.date += timedelta(days=dayDiff)
            return

    def try_create_bookings(self, data):
        if not data['is_recurring']:
            self.create_terms_bookings(data,data['term'])
        else:
            term = data['term']
            self.create_terms_bookings(data,term)
            if term == "September":
                term = "January"
                self.date = get_first_weekday(2025, 1, data['day']).date()
                self.create_terms_bookings(data,term)
            if term == "January":
                term = "May"
                self.date = get_first_weekday(2025, 5, data['day']).date()
                self.create_terms_bookings(data,term)

    def create_terms_bookings(self,data, lesson_term):
        try:
            freq = self.frequencies[randint(0, 2)]
            session_counts = {"Weekly": 15, "Biweekly": 30, "Fortnightly": 7}
            sessions = session_counts.get(freq, 0)
            for i in range(0, sessions):
                self.create_booking(data, freq, lesson_term)
                match freq:
                    case "Weekly":
                        self.date += timedelta(days=7)
                    case "Biweekly":
                        self.determine_biweekly_date(data["day"].day, data["day2"].day)
                    case "Fortnightly":
                        self.date += timedelta(days=14)
        except Exception as e:
            pass

    def create_booking(self, data, freq, lesson_term):
        try:
            booking_object = Booking.objects.create(
                student=data['student'],
                tutor=data['tutor'],
                knowledge_area=data['knowledge_area'],
                term=lesson_term,
                frequency=freq,
                duration=data['duration'],
                is_recurring=data['is_recurring'],
                venue=data['venue'],
                date=self.date,
                day=data['day'],
                title=data['title'],
                cancellation_requested=True if randint(0, 1) else False,
                lesson_identifier=self.lesson_identifier,
            )
        except Exception as e:
            pass