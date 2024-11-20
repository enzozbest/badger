import json
from code_tutors.management.commands.seed_users import add_knowledge_areas
from user_system.models import User, Day, KnowledgeArea

def create_test_user():
    with open('user_system/fixtures/test_users.json', 'r') as file:
        users = json.load(file)

        for user_data in users:
            availability_days = user_data.pop('availability', [])
            knowledge_areas = user_data.pop('knowledge_areas', [])
            user, created = User.objects.get_or_create(**user_data)

            if availability_days:
                update_availability(user, availability_days)

            if user.is_tutor and knowledge_areas:
                add_knowledge_areas(user, knowledge_areas)

def update_availability(user: User, days: list[str]):
    for day_name in days:
        day, _ = Day.objects.get_or_create(day=day_name)
        user.availability.add(day)
        user.save()

def add_knowledge_areas(user: User, areas: list[str]):
    for subject in areas:
        KnowledgeArea.objects.get_or_create(subject=subject, user=user)