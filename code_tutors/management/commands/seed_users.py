from faker import Faker
from django.core.management.base import BaseCommand
from user_system.models import User, KnowledgeArea
from code_tutors.management.helpers import availability_provider
from code_tutors.management.helpers import programming_langs_provider
from random import randint, random

user_fixtures = [
    {'username': '@johndoe', 'email': 'john.doe@example.org', 'first_name': 'John', 'last_name': 'Doe', 'user_type': 'Admin'},
    {'username': '@janedoe', 'email': 'jane.doe@example.org', 'first_name': 'Jane', 'last_name': 'Doe', 'user_type': 'Tutor'},
    {'username': '@charlie', 'email': 'charlie.johnson@example.org', 'first_name': 'Charlie', 'last_name': 'Johnson',
     'user_type': 'Student'},
]

class Command(BaseCommand):
    USER_COUNT = 300
    DEFAULT_PASSWORD = 'Password123'
    help = 'Seeds the database with sample data'

    def __init__(self):
        self.faker = Faker('en_GB')
        self.faker.add_provider(availability_provider.AvailabilityProvider)
        self.faker.add_provider(programming_langs_provider.ProgrammingLangsProvider)
        self.user_types = ['Tutor', 'Student', 'Admin']

    def handle(self, *args, **options):
        self.create_users()
        self.users = User.objects.all()

    def create_users(self):
        self.generate_user_fixtures()
        self.generate_random_users()

    def generate_user_fixtures(self):
        for data in user_fixtures:
            self.try_create_user(data)

    def generate_random_users(self):
        user_count = User.objects.count()
        while user_count < self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
            self.generate_user()
            user_count = User.objects.count()
        print("User seeding complete. \n")

    def generate_user(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = create_email(first_name, last_name)
        username = create_username(first_name, last_name)
        user_type = self.user_types[randint(0, 2)]
        availability = self.faker.availability()
        self.try_create_user({'username': username, 'email': email, 'first_name': first_name, 'last_name': last_name, 'user_type': user_type,
                              'availability': availability})

    def try_create_user(self, data):
        try:
            self.create_user(data)
        except:
            pass

    def create_user(self, data):
        user_obj =User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=Command.DEFAULT_PASSWORD,
            first_name=data['first_name'],
            last_name=data['last_name'],
            user_type=data['user_type'],
        )

        if data['availability']:
            user_obj.availability.set(data['availability'])

        if user_obj.is_tutor:
            add_knowledge_areas(user_obj, random_knowledge_areas(5, self.faker))
            set_hourly_rate(user_obj, 5, 40)

        user_obj.save()


def create_username(first_name, last_name):
    return '@' + first_name.lower() + last_name.lower()

def create_email(first_name, last_name):
    return first_name + '.' + last_name + '@example.org'

def random_knowledge_areas(max: int, faker: Faker) -> list[str]:
    ret = []
    for _ in range(max):
        ret.append(faker.programming_langs())
    return ret

def add_knowledge_areas(tutor: User, areas: list[str]):
    for area in areas:
        if not KnowledgeArea.objects.filter(subject=area, user=tutor).exists():
            obj = KnowledgeArea.objects.create(subject=area, user=tutor)
            obj.save()


def set_hourly_rate(tutor: User, min, max):
    tutor.hourly_rate = round(random.uniform(5.0, 40.0), 2)
    tutor.save()
